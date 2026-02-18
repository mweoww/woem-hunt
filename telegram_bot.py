"""
telegram_bot.py - Telegram Bot Handler dengan kontrol mining
Fitur: /start, /status, /wallet, /balance, /reward, /claim, /stop, /resume, /restart
"""

import os
import sys
import fcntl
import atexit
import asyncio
import threading
import time
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from wallet import get_balance_eth, get_balance_agc, load_wallet
from contracts import get_claimable_rewards, get_agc_balance

# ===== SINGLE INSTANCE LOCK =====
LOCK_FILE = "/tmp/woemhunt_telegram.lock"

def check_single_instance():
    try:
        fp = open(LOCK_FILE, 'w')
        fcntl.flock(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
        def remove_lock():
            try:
                fcntl.flock(fp, fcntl.LOCK_UN)
                fp.close()
                os.remove(LOCK_FILE)
            except:
                pass
        atexit.register(remove_lock)
        return True
    except IOError:
        print("❌ Another telegram instance is already running. Exiting.")
        sys.exit(1)

if os.name != 'nt':
    check_single_instance()

# ===== GLOBAL STATUS =====
mining_status = {
    "running": False,
    "paused": False,
    "total_cycles": 0,
    "solved": 0,
    "errors": 0,
    "last_cycle": None,
    "total_reward": 0,
    "start_time": None,
    "pause_time": None
}

# Referensi ke main loop (akan di-set dari main.py)
mining_loop_control = {
    "should_run": True,
    "should_pause": False,
    "restart_flag": False
}

class TelegramNotifier:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.app = None
        self.loop = None
        self._running = False

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = (
            "🤖 *WOEM-HUNT AGENTCOIN BOT*\n\n"
            "📊 *Perintah Mining:*\n"
            "`/status` - Status mining\n"
            "`/stop` - Hentikan mining sementara\n"
            "`/resume` - Lanjutkan mining\n"
            "`/restart` - Restart mining\n\n"
            "💰 *Perintah Wallet:*\n"
            "`/wallet` - Info wallet\n"
            "`/balance` - Cek balance AGC\n"
            "`/reward` - Total reward\n"
            "`/claim` - Claim reward\n\n"
            "❓ *Lainnya:*\n"
            "`/start` - Pesan ini\n"
            "`/help` - Bantuan"
        )
        await update.message.reply_text(msg, parse_mode='Markdown')

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        wallet_data = load_wallet()
        agent_id = wallet_data.get('agent_id', 'Unknown') if wallet_data else 'No wallet'
        
        # Tentukan status
        if not mining_status['running']:
            status_emoji = "⏸️"
            status_text = "Stopped"
        elif mining_status['paused']:
            status_emoji = "⏸️"
            status_text = "Paused"
        else:
            status_emoji = "✅"
            status_text = "Running"
        
        # Hitung uptime
        uptime = "N/A"
        if mining_status['start_time'] and mining_status['running']:
            start = datetime.strptime(mining_status['start_time'], '%Y-%m-%d %H:%M:%S')
            delta = datetime.now() - start
            hours = delta.seconds // 3600
            minutes = (delta.seconds % 3600) // 60
            uptime = f"{hours}h {minutes}m"
        
        msg = (
            f"📊 *MINING STATUS*\n"
            f"`{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n\n"
            f"🔹 *Agent ID:* `{agent_id}`\n"
            f"🔹 *Status:* {status_emoji} `{status_text}`\n"
            f"🔹 *Uptime:* `{uptime}`\n"
            f"🔹 *Cycles:* `{mining_status['total_cycles']}`\n"
            f"🔹 *Solved:* `{mining_status['solved']}`\n"
            f"🔹 *Errors:* `{mining_status['errors']}`\n"
            f"🔹 *AGC Mined:* `{mining_status['total_reward']}`\n"
        )
        
        if mining_status['last_cycle']:
            msg += f"🔹 *Last Cycle:* `{mining_status['last_cycle']}`"
        
        await update.message.reply_text(msg, parse_mode='Markdown')

    async def stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Hentikan mining sementara"""
        global mining_loop_control
        if not mining_status['running']:
            await update.message.reply_text("❌ Mining sudah berhenti")
            return
        
        if mining_status['paused']:
            await update.message.reply_text("⚠️ Mining sudah di-pause")
            return
        
        mining_loop_control["should_pause"] = True
        mining_status['paused'] = True
        mining_status['pause_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        await update.message.reply_text("⏸️ *Mining dihentikan sementara*\nGunakan /resume untuk melanjutkan", parse_mode='Markdown')

    async def resume_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lanjutkan mining"""
        global mining_loop_control
        if not mining_status['running']:
            await update.message.reply_text("❌ Mining belum dimulai")
            return
        
        if not mining_status['paused']:
            await update.message.reply_text("⚠️ Mining sedang berjalan")
            return
        
        mining_loop_control["should_pause"] = False
        mining_status['paused'] = False
        
        await update.message.reply_text("▶️ *Mining dilanjutkan*", parse_mode='Markdown')

    async def restart_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Restart mining (pause lalu resume otomatis)"""
        global mining_loop_control
        
        await update.message.reply_text("🔄 *Merestart mining...*", parse_mode='Markdown')
        
        # Set flag restart
        mining_loop_control["restart_flag"] = True
        mining_loop_control["should_pause"] = True
        mining_status['paused'] = True
        
        # Tunggu sebentar
        await asyncio.sleep(3)
        
        # Resume
        mining_loop_control["should_pause"] = False
        mining_status['paused'] = False
        mining_loop_control["restart_flag"] = False
        
        await update.message.reply_text("✅ *Restart selesai, mining dilanjutkan*", parse_mode='Markdown')

    async def wallet_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        wallet_data = load_wallet()
        if not wallet_data:
            await update.message.reply_text("❌ Belum ada wallet")
            return
        
        eth = get_balance_eth()
        agc = get_balance_agc()
        
        msg = (
            f"💰 *WALLET INFO*\n\n"
            f"📤 *Address:*\n`{wallet_data['address']}`\n\n"
            f"🔑 *Agent ID:* `{wallet_data.get('agent_id', 'Unknown')}`\n\n"
            f"💎 *Balance:*\n"
            f"  ETH: `{eth:.6f}`\n"
            f"  AGC: `{agc:.2f}`"
        )
        await update.message.reply_text(msg, parse_mode='Markdown')

    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        wallet_data = load_wallet()
        if not wallet_data:
            await update.message.reply_text("❌ Belum ada wallet")
            return
        
        from contracts import get_agc_balance
        from wallet import get_wallet
        account, _ = get_wallet()
        if account:
            agc = get_agc_balance(account)
            await update.message.reply_text(f"💰 *AGC Balance:* `{agc:.2f} AGC`", parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Gagal get account")

    async def reward_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = (
            f"💰 *AGC REWARD*\n\n"
            f"Total mined: `{mining_status['total_reward']} AGC`\n"
        )
        await update.message.reply_text(msg, parse_mode='Markdown')

    async def claim_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("⏳ Claim via /claim akan segera diimplement")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.start_command(update, context)

    async def send_notification(self, message):
        try:
            if self.app:
                await self.app.bot.send_message(
                    chat_id=self.chat_id,
                    text=message,
                    parse_mode='Markdown'
                )
        except Exception as e:
            print(f"❌ Telegram error: {e}")

    def send_sync(self, message):
        if self.loop and self.app and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.send_notification(message),
                self.loop
            )

    async def run_async(self):
        self.app = Application.builder().token(self.token).build()
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        self.app.add_handler(CommandHandler("stop", self.stop_command))
        self.app.add_handler(CommandHandler("resume", self.resume_command))
        self.app.add_handler(CommandHandler("restart", self.restart_command))
        self.app.add_handler(CommandHandler("wallet", self.wallet_command))
        self.app.add_handler(CommandHandler("balance", self.balance_command))
        self.app.add_handler(CommandHandler("reward", self.reward_command))
        self.app.add_handler(CommandHandler("claim", self.claim_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        
        print("🤖 Telegram bot started with control commands!")
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
        
        self._running = True
        while self._running:
            await asyncio.sleep(1)
        
        await self.app.updater.stop()
        await self.app.stop()
        await self.app.shutdown()

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.run_async())
        except KeyboardInterrupt:
            print("🛑 Telegram stopped")
        finally:
            self.loop.close()

    def stop(self):
        self._running = False

telegram_bot = None

def init_telegram():
    global telegram_bot
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram disabled")
        return None
    telegram_bot = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    thread = threading.Thread(target=telegram_bot.run, daemon=True)
    thread.start()
    time.sleep(2)
    return telegram_bot

def send_notification(msg):
    if telegram_bot:
        telegram_bot.send_sync(msg)

def stop_telegram():
    if telegram_bot:
        telegram_bot.stop()

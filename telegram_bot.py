"""
telegram_bot.py - Notifikasi dan command Telegram
"""

import asyncio
import threading
import time
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from wallet import get_balance_eth, get_balance_agc, load_wallet
from contracts import get_claimable_rewards, get_agent_id

mining_status = {
    "running": False,
    "total_cycles": 0,
    "solved": 0,
    "errors": 0,
    "last_cycle": None,
    "total_reward": 0,
    "start_time": None
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
            "`/start` - Pesan ini\n"
            "`/status` - Status mining\n"
            "`/wallet` - Info wallet & balance\n"
            "`/reward` - Total reward\n"
            "`/claim` - Claim reward\n"
            "`/help` - Bantuan"
        )
        await update.message.reply_text(msg, parse_mode='Markdown')

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        wallet_data = load_wallet()
        agent_id = wallet_data.get('agent_id', 'Unknown') if wallet_data else 'No wallet'
        
        msg = (
            f"📊 *MINING STATUS*\n"
            f"`{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n\n"
            f"🔹 *Agent ID:* `{agent_id}`\n"
            f"🔹 *Status:* {'✅ Running' if mining_status['running'] else '⏸️ Idle'}\n"
            f"🔹 *Cycles:* `{mining_status['total_cycles']}`\n"
            f"🔹 *Solved:* `{mining_status['solved']}`\n"
            f"🔹 *Errors:* `{mining_status['errors']}`\n"
            f"🔹 *AGC Mined:* `{mining_status['total_reward']}`"
        )
        await update.message.reply_text(msg, parse_mode='Markdown')

    async def wallet_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        wallet_data = load_wallet()
        if not wallet_data:
            await update.message.reply_text("❌ Belum ada wallet")
            return
        
        eth = get_balance_eth()
        agc = get_balance_agc()
        claimable = get_claimable_rewards(None)  # butuh account
        
        msg = (
            f"💰 *WALLET INFO*\n\n"
            f"📤 *Address:*\n`{wallet_data['address']}`\n\n"
            f"🔑 *Agent ID:* `{wallet_data.get('agent_id', 'Unknown')}`\n\n"
            f"💎 *Balance:*\n"
            f"  ETH: `{eth:.6f}`\n"
            f"  AGC: `{agc:.2f}`\n"
            f"  Claimable: `{claimable:.2f}`"
        )
        await update.message.reply_text(msg, parse_mode='Markdown')

    async def reward_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = (
            f"💰 *AGC REWARD*\n\n"
            f"Total mined: `{mining_status['total_reward']} AGC`\n"
            f"Claimable: `{get_claimable_rewards(None):.2f}`"
        )
        await update.message.reply_text(msg, parse_mode='Markdown')

    async def claim_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("⏳ Processing claim...")
        # Akan diimplement di main

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
        self.app.add_handler(CommandHandler("wallet", self.wallet_command))
        self.app.add_handler(CommandHandler("reward", self.reward_command))
        self.app.add_handler(CommandHandler("claim", self.claim_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        
        print("🤖 Telegram bot started!")
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

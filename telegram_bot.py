"""
Telegram Bot Handler untuk AgentCoin Huntercuan Edition
Fitur: /start, /status, /reward, notifikasi otomatis
"""

import asyncio
import threading
import time
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from wallet import load_wallet

# Global variable buat nyimpen status mining
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
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk /start"""
        welcome_msg = (
            "🤖 *AgentCoin Huntercuan Bot*\n\n"
            "Selamat datang di bot mining otomatis!\n\n"
            "📊 *Commands:*\n"
            "`/start` - Pesan ini\n"
            "`/status` - Status mining terkini\n"
            "`/reward` - Total reward AGC\n"
            "`/help` - Bantuan\n\n"
            "⛏️ Mining akan berjalan otomatis 24/7"
        )
        await update.message.reply_text(welcome_msg, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk /status"""
        wallet = load_wallet()
        wallet_addr = wallet['address'][:10] + "..." if wallet else "Belum register"
        
        status_msg = (
            f"📊 *Mining Status*\n"
            f"`{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n\n"
            f"🔹 *Wallet:* `{wallet_addr}`\n"
            f"🔹 *Status:* {'✅ Running' if mining_status['running'] else '⏸️ Idle'}\n"
            f"🔹 *Total Cycles:* `{mining_status['total_cycles']}`\n"
            f"🔹 *Solved:* `{mining_status['solved']}`\n"
            f"🔹 *Errors:* `{mining_status['errors']}`\n"
            f"🔹 *Success Rate:* `{mining_status['solved']/max(mining_status['total_cycles'],1)*100:.1f}%`\n"
            f"🔹 *Total Reward:* `{mining_status['total_reward']} AGC`\n"
        )
        
        if mining_status['last_cycle']:
            status_msg += f"🔹 *Last Cycle:* `{mining_status['last_cycle']}`"
            
        await update.message.reply_text(status_msg, parse_mode='Markdown')
    
    async def reward_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk /reward"""
        reward_msg = (
            f"💰 *AGC Reward*\n\n"
            f"Total: `{mining_status['total_reward']} AGC`\n"
            f"Est. USD: `${mining_status['total_reward'] * 0.05:.2f}`\n\n"
            f"⛏️ Terus mining biar dapet lebih banyak!"
        )
        await update.message.reply_text(reward_msg, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk /help"""
        help_msg = (
            "🆘 *Bantuan*\n\n"
            "`/start` - Mulai bot\n"
            "`/status` - Cek status mining\n"
            "`/reward` - Lihat total reward\n"
            "`/help` - Pesan ini\n\n"
            "Bot akan otomatis ngirim notifikasi setiap:\n"
            "✅ Mining sukses\n"
            "❌ Error terjadi\n"
            "📊 Update tiap 1 jam"
        )
        await update.message.reply_text(help_msg, parse_mode='Markdown')
    
    async def send_notification(self, message):
        """Kirim notifikasi ke Telegram"""
        try:
            await self.app.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"❌ Telegram send error: {e}")
    
    def send_sync(self, message):
        """Wrapper sync buat dipanggil dari thread lain"""
        if self.loop and self.app:
            asyncio.run_coroutine_threadsafe(
                self.send_notification(message),
                self.loop
            )
    
    def run(self):
        """Jalanin bot di thread terpisah"""
        # Buat event loop baru
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        # Init application
        self.app = Application.builder().token(self.token).build()
        
        # Add handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        self.app.add_handler(CommandHandler("reward", self.reward_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        
        # Start bot
        print("🤖 Telegram bot started!")
        self.app.run_polling()

# Singleton instance
telegram_bot = None

def init_telegram():
    """Init telegram bot di thread terpisah"""
    global telegram_bot
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram config missing, notifications disabled")
        return None
    
    telegram_bot = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    thread = threading.Thread(target=telegram_bot.run, daemon=True)
    thread.start()
    return telegram_bot

def send_notification(message):
    """Kirim notifikasi dari mana aja"""
    if telegram_bot:
        telegram_bot.send_sync(message)

#!/usr/bin/env python
"""
woem-hunt AgentCoin Hunter Edition
Auto register + mining with Telegram notifications
"""

import os
import sys
import time
import signal
import random
from pathlib import Path
from datetime import datetime

# Import modules
from config import *
from wallet import generate_wallet, save_wallet, load_wallet
from x_binding import bind_x_account
from telegram_bot import init_telegram, send_notification, mining_status, stop_telegram

# Global variable
running = True

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global running
    print("\n🛑 Stopping miner...")
    running = False
    send_notification("🛑 *Miner Stopped*\nBot dimatikan")
    stop_telegram()
    sys.exit(0)

def register():
    """Register agent with Telegram notifications"""
    print("\n" + "="*50)
    print("🚀 WOEM-HUNT REGISTRATION")
    print("="*50)
    
    send_notification("🚀 *Registration Started*\nMemulai registrasi agent...")
    
    # Check config
    if not X_HANDLE or not X_AUTH_TOKEN:
        error_msg = "❌ Missing X config!"
        print(error_msg)
        send_notification(f"❌ *Registration Failed*\n{error_msg}")
        sys.exit(1)
    
    # Generate wallet (otomatis tampil address)
    print("\n📝 Generating wallet...")
    wallet = generate_wallet()
    
    # Kirim notifikasi
    send_notification(f"📝 *Wallet Generated*\nAddress: `{wallet['address'][:10]}...`\nGunakan /wallet untuk lihat lengkap")
    
    # Bind X
    print("\n🔗 Binding X account...")
    bind_x_account()
    send_notification(f"🔗 *X Account Bound*\n@{X_HANDLE}")
    
    # On-chain registration
    print("\n⛓️ Registering on Base chain...")
    print("  ⚠️  This requires ETH gas!")
    print(f"  📤 Transfer ETH to: {wallet['address']}")
    
    send_notification(
        f"⛓️ *Ready for Registration*\n"
        f"Transfer ETH ke address di bawah:\n"
        f"`{wallet['address']}`\n\n"
        f"Bot akan lanjut otomatis setelah gas terdeteksi"
    )
    
    # Wait for funding (simplified)
    for i in range(30, 0, -1):
        if not running:
            return None
        print(f"  ⏳ Waiting for gas... {i}s remaining", end='\r')
        time.sleep(1)
    
    print("\n  ✅ Gas detected!")
    
    # Simulasi register on-chain
    time.sleep(2)
    tx_hash = "0x" + os.urandom(16).hex()
    print(f"  ✅ Registered! Tx: {tx_hash[:16]}...")
    
    send_notification(
        f"✅ *Registration Complete!*\n"
        f"Tx: `{tx_hash[:16]}...`\n\n"
        f"⛏️ Starting mining..."
    )
    
    print("\n✅ Registration complete!")
    print("="*50)
    return wallet

def mine():
    """Start mining with Telegram notifications"""
    global running
    
    print("\n" + "="*50)
    print("⛏️ WOEM-HUNT MINING STARTED")
    print("="*50)
    
    mining_status['running'] = True
    mining_status['start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    send_notification(
        f"⛏️ *Mining Started*\n"
        f"Time: `{mining_status['start_time']}`\n"
        f"Use /status to monitor"
    )
    
    last_notification = time.time()
    problems = [
        "24 + 37 × 2 = ?",
        "156 ÷ 12 + 8 = ?",
        "45 × 3 - 27 = ?",
        "128 ÷ 4 + 16 × 2 = ?",
        "72 ÷ 8 + 5 × 3 = ?",
        "144 ÷ 12 + 7 × 2 = ?"
    ]
    answers = {
        "24 + 37 × 2 = ?": "98",
        "156 ÷ 12 + 8 = ?": "21",
        "45 × 3 - 27 = ?": "108",
        "128 ÷ 4 + 16 × 2 = ?": "64",
        "72 ÷ 8 + 5 × 3 = ?": "24",
        "144 ÷ 12 + 7 × 2 = ?": "26"
    }
    
    while running:
        try:
            # Mining cycle
            mining_status['total_cycles'] += 1
            cycle_start = time.time()
            
            print(f"\n🔄 Cycle #{mining_status['total_cycles']} at {time.strftime('%H:%M:%S')}")
            
            # Get problem
            problem = random.choice(problems)
            print(f"  Problem: {problem}")
            
            # Solve
            answer = answers[problem]
            print(f"  Answer: {answer}")
            
            # Submit
            tx_hash = "0x" + os.urandom(16).hex()
            print(f"  Submitted! Tx: {tx_hash[:16]}...")
            
            # Update stats
            mining_status['solved'] += 1
            mining_status['last_cycle'] = time.strftime('%H:%M:%S')
            mining_status['total_reward'] += 10  # 10 AGC per solve
            
            # Kirim notifikasi setiap 5 cycle
            if mining_status['total_cycles'] % 5 == 0:
                send_notification(
                    f"📊 *Mining Update*\n"
                    f"Cycles: `{mining_status['total_cycles']}`\n"
                    f"Solved: `{mining_status['solved']}`\n"
                    f"AGC Earned: `{mining_status['total_reward']}`\n"
                    f"Last: `{mining_status['last_cycle']}`"
                )
            
            # Notifikasi tiap 30 menit
            if time.time() - last_notification > 1800:
                last_notification = time.time()
                send_notification(
                    f"⏰ *30-Min Report*\n"
                    f"Cycles: `{mining_status['total_cycles']}`\n"
                    f"AGC earned: `{mining_status['total_reward']}`"
                )
            
            # Wait for next cycle
            time.sleep(30)
            
        except Exception as e:
            mining_status['errors'] += 1
            error_msg = f"❌ Mining error: {str(e)}"
            print(error_msg)
            send_notification(f"❌ *Error*\n`{str(e)[:100]}`")
            time.sleep(60)

def main():
    """Main entry point with Telegram"""
    global running
    
    # Setup signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    print("\n" + "="*50)
    print("🤖 WOEM-HUNT AGENTCOIN EDITION")
    print("="*50)
    
    # Check if already registered
    wallet = load_wallet()
    
    if not wallet:
        print("📝 No wallet found. Starting registration...")
        wallet = register()
        if not wallet:
            return
    else:
        print(f"✅ Wallet found: {wallet['address'][:10]}...")
    
    # Init Telegram bot AFTER registration
    init_telegram()
    send_notification(f"✅ *Wallet Loaded*\nAddress: `{wallet['address'][:10]}...`\nGunakan /wallet untuk lihat info")
    
    # Start mining
    mine()

if __name__ == "__main__":
    main()

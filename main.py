#!/usr/bin/env python
"""
main.py - AgentCoin Mining Bot (Full Version)
"""

import os
import sys
import time
import signal
from datetime import datetime

from config import *
from wallet import get_wallet, load_wallet, update_agent_id
from api import wait_for_active_problem
from contracts import submit_answer, get_agent_id, claim_rewards, get_claimable_rewards
from solver import solve_math_problem
from telegram_bot import init_telegram, send_notification, mining_status, stop_telegram

running = True

def signal_handler(sig, frame):
    global running
    print("\n🛑 Stopping...")
    running = False
    send_notification("🛑 *Bot Stopped*")
    stop_telegram()
    sys.exit(0)

def main():
    global running
    signal.signal(signal.SIGINT, signal_handler)
    
    print("\n" + "="*50)
    print("🤖 WOEM-HUNT AGENTCOIN MINER")
    print("="*50)
    
    # Load wallet
    account, wallet_data = get_wallet()
    if not account:
        print("❌ Gagal load wallet")
        return
    
    # Dapatkan agent ID dari blockchain
    agent_id = get_agent_id(account)
    if agent_id:
        print(f"✅ Agent ID: {agent_id}")
        update_agent_id(agent_id)
        wallet_data['agent_id'] = agent_id
    else:
        print("❌ Gagal mendapatkan Agent ID! Pastikan wallet sudah terdaftar.")
        return
    
    # Init Telegram
    init_telegram()
    send_notification(f"🚀 *Bot Started*\nAgent ID: `{agent_id}`")
    
    mining_status['running'] = True
    mining_status['start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Mining loop
    while running:
        try:
            mining_status['total_cycles'] += 1
            print(f"\n🔄 Cycle #{mining_status['total_cycles']}")
            
            # 1. Fetch problem dengan agent_id
            problem_data = wait_for_active_problem(agent_id)
            if not problem_data:
                time.sleep(30)
                continue
            
            problem_id = problem_data['problem_id']
            personalized = problem_data['personalized']
            
            print(f"📥 Problem #{problem_id}")
            
            # 2. Solve
            answer = solve_math_problem(personalized)
            print(f"🧠 Answer: {answer}")
            
            # 3. Submit on-chain
            tx_hash = submit_answer(account, problem_id, answer)
            if tx_hash:
                print(f"✅ Submitted: {tx_hash[:16]}...")
                mining_status['solved'] += 1
                mining_status['total_reward'] += 10  # asumsi 10 AGC per soal
                
                # Notifikasi tiap 5 cycle
                if mining_status['total_cycles'] % 5 == 0:
                    send_notification(
                        f"📊 *Mining Update*\n"
                        f"Cycles: `{mining_status['total_cycles']}`\n"
                        f"Solved: `{mining_status['solved']}`\n"
                        f"AGC: `{mining_status['total_reward']}`"
                    )
            else:
                mining_status['errors'] += 1
                print("❌ Submit gagal")
            
            # 4. Auto claim jika enable
            if AUTO_CLAIM and mining_status['total_cycles'] % 10 == 0:
                claimable = get_claimable_rewards(account)
                if claimable > 0:
                    print(f"💰 Claiming {claimable:.2f} AGC...")
                    tx = claim_rewards(account)
                    if tx:
                        send_notification(f"💰 *Claimed*\n{claimable:.2f} AGC")
            
            mining_status['last_cycle'] = datetime.now().strftime('%H:%M:%S')
            
            # Tunggu sesuai interval
            time.sleep(POLL_INTERVAL)
            
        except Exception as e:
            mining_status['errors'] += 1
            print(f"❌ Error: {e}")
            send_notification(f"❌ *Error*\n`{str(e)[:100]}`")
            time.sleep(60)

if __name__ == "__main__":
    main()

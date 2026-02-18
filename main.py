#!/usr/bin/env python
"""
main.py - AgentCoin Mining Bot (Anti Revert Version)
"""

import os
import sys
import time
import signal
from datetime import datetime

from config import *
from wallet import get_wallet, load_wallet, update_agent_id
from api import wait_for_active_problem
from contracts import submit_answer, get_agent_id, claim_rewards, get_claimable_rewards, check_already_submitted
from solver import solve_math_problem
from telegram_bot import init_telegram, send_notification, mining_status, stop_telegram

running = True
submitted_problems = set()  # Track submitted problems

def signal_handler(sig, frame):
    global running
    print("\n🛑 Stopping...")
    running = False
    send_notification("🛑 *Bot Stopped*")
    stop_telegram()
    sys.exit(0)

def main():
    global running, submitted_problems
    signal.signal(signal.SIGINT, signal_handler)
    
    print("\n" + "="*50)
    print("🤖 WOEM-HUNT AGENTCOIN MINER (ANTI-REVERT)")
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
    
    # Init Telegram (COMMENT DULU SAMPAI STABIL)
    # init_telegram()
    # send_notification(f"🚀 *Bot Started*\nAgent ID: `{agent_id}`")
    
    mining_status['running'] = True
    mining_status['start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    last_problem_id = None
    same_problem_count = 0
    
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
            
            # CEK: Problem sama berulang?
            if problem_id == last_problem_id:
                same_problem_count += 1
                if same_problem_count > 3:
                    print(f"⚠️ Problem #{problem_id} muncul terus, tunggu 5 menit...")
                    time.sleep(300)
                    same_problem_count = 0
                    continue
            else:
                same_problem_count = 0
                last_problem_id = problem_id
            
            # CEK: Udah pernah di-submit?
            if problem_id in submitted_problems:
                print(f"⚠️ Problem #{problem_id} sudah pernah di-submit, skip...")
                time.sleep(POLL_INTERVAL)
                continue
            
            print(f"📥 Problem #{problem_id}")
            
            # 2. Solve
            answer = solve_math_problem(personalized)
            print(f"🧠 Answer: {answer}")
            
            # 3. Submit on-chain (dengan pengecekan)
            tx_hash = submit_answer(account, problem_id, answer)
            if tx_hash:
                print(f"✅ Submitted: {tx_hash[:16]}...")
                mining_status['solved'] += 1
                mining_status['total_reward'] += 10
                submitted_problems.add(problem_id)  # Tandai sudah submit
            else:
                mining_status['errors'] += 1
                print("❌ Submit gagal, coba problem lain")
            
            mining_status['last_cycle'] = datetime.now().strftime('%H:%M:%S')
            
            # Tunggu sesuai interval
            time.sleep(POLL_INTERVAL)
            
        except Exception as e:
            mining_status['errors'] += 1
            print(f"❌ Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()

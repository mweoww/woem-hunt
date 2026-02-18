#!/usr/bin/env python
"""
main.py - AgentCoin Mining Bot dengan kontrol Telegram
Fitur: /stop, /resume, /restart via Telegram
"""

import os
import sys
import time
import signal
from datetime import datetime

from config import *
from wallet import get_wallet, load_wallet, update_agent_id
from api import wait_for_active_problem
from contracts import submit_answer, get_agent_id, get_agc_balance
from solver import solve_math_problem
from telegram_bot import init_telegram, send_notification, mining_status, stop_telegram, mining_loop_control

running = True
submitted_problems = set()

def signal_handler(sig, frame):
    global running
    print("\n🛑 Stopping...")
    running = False
    send_notification("🛑 *Bot Stopped*")
    stop_telegram()
    sys.exit(0)

def mining_loop(account, agent_id):
    """Loop mining utama dengan kontrol pause/resume"""
    global running, submitted_problems
    
    mining_status['running'] = True
    mining_status['start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    last_problem_id = None
    same_problem_count = 0
    
    while running:
        try:
            # Cek apakah harus pause
            while mining_loop_control["should_pause"] and running:
                if mining_loop_control["restart_flag"]:
                    print("🔄 Restarting...")
                    # Reset state
                    submitted_problems.clear()
                    last_problem_id = None
                    mining_loop_control["restart_flag"] = False
                time.sleep(2)
            
            mining_status['total_cycles'] += 1
            print(f"\n🔄 Cycle #{mining_status['total_cycles']}")
            
            # Fetch problem
            problem_data = wait_for_active_problem(agent_id)
            if not problem_data:
                time.sleep(30)
                continue
            
            problem_id = problem_data['problem_id']
            personalized = problem_data['personalized']
            
            # Skip problem yang sama
            if problem_id == last_problem_id:
                same_problem_count += 1
                if same_problem_count > 2:
                    print(f"⚠️ Problem #{problem_id} muncul terus, tunggu...")
                    time.sleep(120)
                    same_problem_count = 0
                    continue
            else:
                same_problem_count = 0
                last_problem_id = problem_id
            
            if problem_id in submitted_problems:
                print(f"⚠️ Problem #{problem_id} sudah diproses, skip")
                time.sleep(POLL_INTERVAL)
                continue
            
            print(f"📥 Problem #{problem_id}")
            
            # Solve
            answer = solve_math_problem(personalized)
            print(f"🧠 Answer: {answer}")
            
            # Submit
            tx_hash = submit_answer(account, problem_id, answer)
            if tx_hash:
                print(f"✅ Submitted: {tx_hash[:16]}...")
                mining_status['solved'] += 1
                mining_status['total_reward'] += 10
                submitted_problems.add(problem_id)
                send_notification(f"✅ *Mined*\nProblem #{problem_id}\nAGC: +10")
            else:
                mining_status['errors'] += 1
                print("❌ Submit gagal")
                submitted_problems.add(problem_id)  # Tandai gagal juga
            
            mining_status['last_cycle'] = datetime.now().strftime('%H:%M:%S')
            time.sleep(POLL_INTERVAL)
            
        except Exception as e:
            mining_status['errors'] += 1
            print(f"❌ Error: {e}")
            send_notification(f"❌ *Error*\n`{str(e)[:100]}`")
            time.sleep(60)

def main():
    global running
    
    signal.signal(signal.SIGINT, signal_handler)
    
    print("\n" + "="*60)
    print("🤖 WOEM-HUNT AGENTCOIN MINER (DENGAN KONTROL TELEGRAM)")
    print("="*60)
    
    # Load wallet
    account, wallet_data = get_wallet()
    if not account:
        print("❌ Gagal load wallet")
        return
    
    # Dapatkan agent ID
    agent_id = get_agent_id(account)
    if agent_id:
        print(f"✅ Agent ID: {agent_id}")
        update_agent_id(agent_id)
        wallet_data['agent_id'] = agent_id
    else:
        print("❌ Gagal mendapatkan Agent ID!")
        return
    
    # CEK Balance AGC
    agc_balance = get_agc_balance(account)
    print(f"💰 AGC Balance: {agc_balance}")
    if agc_balance < 100:
        print(f"⚠️ Balance AGC {agc_balance} < 100, mungkin tidak bisa submit")
    
    # Init Telegram
    init_telegram()
    send_notification(
        f"🚀 *Bot Started*\n"
        f"Agent ID: `{agent_id}`\n"
        f"AGC: `{agc_balance}`\n\n"
        f"Perintah: /stop, /resume, /restart, /status"
    )
    
    # Mulai mining loop
    mining_loop(account, agent_id)

if __name__ == "__main__":
    main()

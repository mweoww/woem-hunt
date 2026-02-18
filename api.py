"""
api.py - Interaksi dengan API AgentCoin
"""

import requests
import time
from config import AGC_API_URL

processed_problems = set()

def get_current_problem():
    url = f"{AGC_API_URL}/api/problem/current"
    max_retries = 3
    for i in range(max_retries):
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 503:
                wait = 2**i * 30
                print(f"⚠️ API 503, tunggu {wait}s...")
                time.sleep(wait)
            else:
                print(f"⚠️ API error: {resp.status_code}")
                time.sleep(30)
        except Exception as e:
            print(f"⚠️ API request failed: {e}")
            time.sleep(2**i * 10)
    return None

def wait_for_active_problem(agent_id):
    wait_count = 0
    while True:
        data = get_current_problem()
        if data and data.get('is_active'):
            problem_id = data['problem_id']
            if problem_id in processed_problems:
                time.sleep(10)
                continue
            template = data['template_text']
            personalized = template.replace("{AGENT_ID}", str(agent_id))
            data['personalized'] = personalized
            processed_problems.add(problem_id)
            return data
        wait_count += 1
        if wait_count % 5 == 0:
            print("⏳ Menunggu problem baru...")
        time.sleep(30)

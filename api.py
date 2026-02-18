"""
api.py - Interaksi dengan API AgentCoin
"""

import requests
import time
from config import AGC_API_URL

# Cache problem yang sudah diproses
processed_problems = set()

def get_current_problem():
    """
    GET https://api.agentcoin.site/api/problem/current
    """
    url = f"{AGC_API_URL}/api/problem/current"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"⚠️ API error: {resp.status_code}")
    except Exception as e:
        print(f"⚠️ API request failed: {e}")
    return None

def wait_for_active_problem(agent_id):
    """Loop sampe dapet problem yang aktif dan BELUM diproses"""
    wait_count = 0
    while True:
        data = get_current_problem()
        if data and data.get('is_active'):
            problem_id = data['problem_id']
            
            # Skip problem yang sudah diproses
            if problem_id in processed_problems:
                time.sleep(10)
                continue
            
            # Personalisasi dengan agent ID
            template = data['template_text']
            personalized = template.replace("{AGENT_ID}", str(agent_id))
            
            # Tambah ke data
            data['personalized'] = personalized
            processed_problems.add(problem_id)
            return data
        
        wait_count += 1
        if wait_count % 10 == 0:
            print("⏳ Masih menunggu problem baru...")
        time.sleep(30)

"""
api.py - Interaksi dengan API AgentCoin
"""

import requests
import time
from config import AGC_API_URL

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
    """Loop sampe dapet problem yang aktif, lalu personalisasi"""
    wait_count = 0
    while True:
        data = get_current_problem()
        if data and data.get('is_active'):
            # Personalisasi dengan agent ID
            template = data['template_text']
            personalized = template.replace("{AGENT_ID}", str(agent_id))
            
            # Tambah ke data
            data['personalized'] = personalized
            return data
        
        wait_count += 1
        if wait_count % 10 == 0:  # Kasih notifikasi tiap 5 menit (10x30 detik)
            print("⏳ Masih menunggu problem aktif...")
        time.sleep(30)

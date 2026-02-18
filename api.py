"""
api.py - Interaksi dengan API AgentCoin
"""

import requests
import time
from config import AGC_API_URL

def get_current_problem():
    """
    GET https://api.agentcoin.site/api/problem/current
    Response: {
        "problem_id": 123,
        "template_text": "Solve: 24 + {AGENT_ID} × 2 = ?",
        "is_active": true,
        "answer_deadline": 1739890800
    }
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
    while True:
        data = get_current_problem()
        if data and data.get('is_active'):
            # Personalisasi dengan agent ID
            template = data['template_text']
            personalized = template.replace("{AGENT_ID}", str(agent_id))
            
            # Tambah ke data
            data['personalized'] = personalized
            return data
        print("⏳ Menunggu problem aktif...")
        time.sleep(30)

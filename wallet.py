"""
wallet.py - Wallet management (from private key)
"""

from eth_account import Account
import json
from pathlib import Path
from web3 import Web3
from config import PRIVATE_KEY, BASE_RPC_URL, AGC_TOKEN_ADDRESS

STATE_FILE = Path("data") / ".state.json"

def get_wallet():
    """Load wallet dari private key"""
    try:
        # Hapus '0x' kalau ada
        clean_key = PRIVATE_KEY.replace('0x', '')
        account = Account.from_key(clean_key)
        
        # Cek apakah sudah ada file state
        wallet_data = load_wallet()
        if not wallet_data:
            wallet_data = {
                "address": account.address,
                "private_key": PRIVATE_KEY,
                "agent_id": None
            }
            save_wallet(wallet_data)
            print(f"✅ Wallet baru disimpan: {account.address[:10]}...")
        else:
            # JANGAN print tiap kali, nanti spam
            pass
            
        return account, wallet_data
    except Exception as e:
        print(f"❌ Gagal load wallet: {e}")
        return None, None

def save_wallet(wallet_data):
    """Simpan wallet data ke file"""
    Path("data").mkdir(exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(wallet_data, f, indent=2)

def load_wallet():
    """Load wallet data dari file"""
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return None

def update_agent_id(agent_id):
    """Update agent ID di state file"""
    wallet_data = load_wallet() or {}
    wallet_data["agent_id"] = agent_id
    save_wallet(wallet_data)

def get_balance_eth():
    """Cek balance ETH"""
    try:
        w3 = Web3(Web3.HTTPProvider(BASE_RPC_URL))
        account, _ = get_wallet()
        if account:
            balance_wei = w3.eth.get_balance(account.address)
            return w3.from_wei(balance_wei, 'ether')
    except:
        pass
    return 0

def get_balance_agc():
    """Cek balance AGC token"""
    try:
        w3 = Web3(Web3.HTTPProvider(BASE_RPC_URL))
        account, _ = get_wallet()
        
        abi = '[{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"}]'
        contract = w3.eth.contract(address=AGC_TOKEN_ADDRESS, abi=abi)
        
        balance = contract.functions.balanceOf(account.address).call()
        return balance / 1e18
    except:
        return 0

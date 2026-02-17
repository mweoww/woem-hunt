from eth_account import Account
import json
from pathlib import Path

STATE_FILE = Path("data") / ".state.json"

def generate_wallet():
    """Generate wallet baru"""
    account = Account.create()
    return {
        "address": account.address,
        "private_key": account.key.hex()
    }

def save_wallet(wallet_data):
    """Simpan wallet ke file"""
    Path("data").mkdir(exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(wallet_data, f, indent=2)
    print(f"✅ Wallet saved: {wallet_data['address'][:10]}...")

def load_wallet():
    """Load wallet dari file"""
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return None

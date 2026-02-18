from eth_account import Account
import json
from pathlib import Path

STATE_FILE = Path("data") / ".state.json"

def generate_wallet():
    """Generate wallet baru"""
    account = Account.create()
    wallet_data = {
        "address": account.address,
        "private_key": account.key.hex()
    }
    
    # Simpan ke file
    save_wallet(wallet_data)
    
    # Tampilkan dengan jelas
    print("\n" + "="*60)
    print("🔐 WALLET ADDRESS - TRANSFER ETH KE SINI!")
    print("="*60)
    print(f"📤 Address    : {account.address}")
    print(f"🔑 Private Key: {account.key.hex()}")
    print("="*60)
    print("⚠️  Kirim minimal 0.001 ETH ke address di atas")
    print("⚠️  Pastikan pake BASE chain (bukan Ethereum mainnet)")
    print("="*60 + "\n")
    
    return wallet_data

def save_wallet(wallet_data):
    """Simpan wallet ke file"""
    Path("data").mkdir(exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(wallet_data, f, indent=2)
    print(f"✅ Wallet saved to {STATE_FILE}")

def load_wallet():
    """Load wallet dari file"""
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return None

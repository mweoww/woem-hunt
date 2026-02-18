"""
wallet.py - Generate dan manage wallet
Prioritas: PRIVATE_KEY dari env > file existing > generate baru
"""

from eth_account import Account
import json
from pathlib import Path
from config import PRIVATE_KEY

STATE_FILE = Path("data") / ".state.json"

def generate_wallet():
    """Generate wallet baru (fallback kalau gak ada PK)"""
    print("\n📝 Generating new wallet...")
    account = Account.create()
    wallet_data = {
        "address": account.address,
        "private_key": account.key.hex()
    }
    
    # Simpan ke file
    save_wallet(wallet_data)
    
    # Tampilkan dengan jelas
    print("\n" + "="*70)
    print("🔐 WALLET ADDRESS - TRANSFER ETH KE SINI!")
    print("="*70)
    print(f"📤 Address    : {account.address}")
    print(f"🔑 Private Key: {account.key.hex()}")
    print("="*70)
    print("⚠️  Kirim minimal 0.001 ETH ke address di atas")
    print("⚠️  Pastikan pake BASE chain (bukan Ethereum mainnet)")
    print("="*70 + "\n")
    
    return wallet_data

def import_wallet_from_env():
    """Import wallet dari private key di environment variable"""
    if not PRIVATE_KEY:
        print("⚠️  PRIVATE_KEY tidak ditemukan di environment, generate wallet baru...")
        return generate_wallet()
    
    try:
        # Hapus '0x' kalau ada
        clean_key = PRIVATE_KEY.replace('0x', '')
        account = Account.from_key(clean_key)
        
        wallet_data = {
            "address": account.address,
            "private_key": PRIVATE_KEY  # simpan dengan format asli
        }
        
        # Simpan ke file
        save_wallet(wallet_data)
        
        print("\n" + "="*70)
        print("🔐 WALLET IMPORTED FROM ENVIRONMENT")
        print("="*70)
        print(f"📤 Address    : {account.address}")
        print(f"🔑 Private Key: {PRIVATE_KEY[:10]}...{PRIVATE_KEY[-6:]}")
        print("="*70)
        print("✅ Wallet imported successfully!")
        print("="*70 + "\n")
        
        return wallet_data
    except Exception as e:
        print(f"❌ Gagal import wallet dari environment: {e}")
        print("📝 Generate wallet baru sebagai fallback...")
        return generate_wallet()

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
            data = json.load(f)
            # Force lowercase biar konsisten
            data['address'] = data['address'].lower()
            return data
    return None

def get_wallet():
    """Main function untuk dapetin wallet (prioritas: env > file > generate)"""
    # Coba load dari file dulu
    wallet = load_wallet()
    if wallet:
        print(f"✅ Wallet loaded from file: {wallet['address'][:10]}...")
        return wallet
    
    # Kalau gak ada, import dari env
    print("📝 No wallet file found. Importing from environment...")
    return import_wallet_from_env()

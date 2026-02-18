"""
config.py - Konfigurasi dari environment variable
"""

import os
import sys
from pathlib import Path

print("🔍 DEBUG: Reading environment variables...")

# X (Twitter) - optional, untuk binding
X_HANDLE = os.environ.get("X_HANDLE", "")
X_AUTH_TOKEN = os.environ.get("X_AUTH_TOKEN", "")
X_CT0 = os.environ.get("X_CT0", "")

# Claude AI (optional, untuk auto-solve)
ANTHROPIC_AUTH_TOKEN = os.environ.get("ANTHROPIC_AUTH_TOKEN", "")

# Telegram
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# ===== AGENTCOIN CORE =====
# Private key (wajib!)
PRIVATE_KEY = os.environ.get("PRIVATE_KEY") or os.environ.get("AGC_PRIVATE_KEY", "")

# RPC
BASE_RPC_URL = os.environ.get("BASE_RPC_URL", "https://mainnet.base.org")
AGC_API_URL = os.environ.get("AGC_API_URL", "https://api.agentcoin.site")

# Contract addresses (dari SKILL.md)
PROBLEM_MANAGER_ADDRESS = os.environ.get(
    "PROBLEM_MANAGER_ADDRESS", 
    "0x7D563ae2881D2fC72f5f4c66334c079B4Cc051c6"
)
AGENT_REGISTRY_ADDRESS = os.environ.get(
    "AGENT_REGISTRY_ADDRESS",
    "0x5A899d52C9450a06808182FdB1D1e4e23AdFe04D"
)
REWARD_DISTRIBUTOR_ADDRESS = os.environ.get(
    "REWARD_DISTRIBUTOR_ADDRESS",
    "0xD85aCAC804c074d3c57A422d26bAfAF04Ed6b899"
)
AGC_TOKEN_ADDRESS = os.environ.get(
    "AGC_TOKEN_ADDRESS",
    "0x48778537634Fa47Ff9CDBFdcEd92F3B9DB50bd97"
)

# Mining settings
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", "60"))  # detik
AUTO_CLAIM = os.environ.get("AUTO_CLAIM", "true").lower() == "true"

print("\n🔍 WOEM-HUNT CONFIG CHECK:")
print(f"  PRIVATE_KEY: {'✅' if PRIVATE_KEY else '❌'}")
print(f"  BASE_RPC_URL: {BASE_RPC_URL}")
print(f"  POLL_INTERVAL: {POLL_INTERVAL}s")
print(f"  AUTO_CLAIM: {AUTO_CLAIM}")
print(f"  TELEGRAM: {'✅' if TELEGRAM_BOT_TOKEN else '❌'}")
print("="*50)

if not PRIVATE_KEY:
    print("❌ FATAL: PRIVATE_KEY tidak ditemukan di environment!")
    sys.exit(1)

"""
config.py - Konfigurasi dari environment variable
"""

import os
import sys
from pathlib import Path

# LANGSUNG baca dari environment variable (Railway)
print("🔍 DEBUG: Reading environment variables...")

# X (Twitter)
X_HANDLE = os.environ.get("X_HANDLE", "")
X_AUTH_TOKEN = os.environ.get("X_AUTH_TOKEN", "")
X_CT0 = os.environ.get("X_CT0", "")

# Claude AI
ANTHROPIC_AUTH_TOKEN = os.environ.get("ANTHROPIC_AUTH_TOKEN", "")

# Telegram
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# PRIVATE KEY (diambil dari Railway Variables)
PRIVATE_KEY = os.environ.get("PRIVATE_KEY", "")

# Debug: cek apakah kebaca
print("\n🔍 WOEM-HUNT CONFIG CHECK:")
print(f"  X_HANDLE: {'✅' if X_HANDLE else '❌'} ({X_HANDLE})")
print(f"  X_AUTH_TOKEN: {'✅' if X_AUTH_TOKEN else '❌'}")
print(f"  ANTHROPIC: {'✅' if ANTHROPIC_AUTH_TOKEN else '❌'}")
print(f"  TELEGRAM: {'✅' if TELEGRAM_BOT_TOKEN else '❌'}")
print(f"  PRIVATE_KEY: {'✅' if PRIVATE_KEY else '❌'}")
print("="*50)

# Kalau masih kosong, kasih warning
if not X_HANDLE or not X_AUTH_TOKEN:
    print("⚠️  WARNING: X config missing, tapi lanjut dulu buat debug")

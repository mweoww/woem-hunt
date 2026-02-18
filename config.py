import os
import sys
from pathlib import Path

# LANGSUNG baca dari environment variable (Railway)
# JANGAN PAKE load_dotenv dulu

print("🔍 DEBUG: Reading environment variables...")
print(f"  All env keys: {list(os.environ.keys())}")

# X (Twitter)
X_HANDLE = os.environ.get("X_HANDLE", "")
X_AUTH_TOKEN = os.environ.get("X_AUTH_TOKEN", "")
X_CT0 = os.environ.get("X_CT0", "")

# Claude AI
ANTHROPIC_AUTH_TOKEN = os.environ.get("ANTHROPIC_AUTH_TOKEN", "")

# Telegram
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# Debug: cek apakah kebaca
print("\n🔍 WOEM-HUNT CONFIG CHECK:")
print(f"  X_HANDLE: {'✅' if X_HANDLE else '❌'} ({X_HANDLE})")
print(f"  X_AUTH_TOKEN: {'✅' if X_AUTH_TOKEN else '❌'}")
print(f"  ANTHROPIC: {'✅' if ANTHROPIC_AUTH_TOKEN else '❌'}")
print(f"  TELEGRAM: {'✅' if TELEGRAM_BOT_TOKEN else '❌'}")
print("="*50)

# Kalau masih kosong, kasih warning tapi jangan exit dulu
if not X_HANDLE or not X_AUTH_TOKEN:
    print("⚠️  WARNING: X config missing, tapi lanjut dulu buat debug")

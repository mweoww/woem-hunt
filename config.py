import os
from dotenv import load_dotenv

# Load .env kalau ada (buat lokal)
load_dotenv()

# Baca dari environment (Railway priority)
X_HANDLE = os.environ.get("X_HANDLE", "")
X_AUTH_TOKEN = os.environ.get("X_AUTH_TOKEN", "")
ANTHROPIC_AUTH_TOKEN = os.environ.get("ANTHROPIC_AUTH_TOKEN", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# Debug: cek config
print("🔍 HUNTERCUAN CONFIG CHECK:")
print(f"  X_HANDLE: {'✅' if X_HANDLE else '❌'}")
print(f"  X_AUTH_TOKEN: {'✅' if X_AUTH_TOKEN else '❌'}")
print(f"  ANTHROPIC: {'✅' if ANTHROPIC_AUTH_TOKEN else '❌'}")
print(f"  TELEGRAM: {'✅' if TELEGRAM_BOT_TOKEN else '❌'}")
print("="*50)

"""Telegram-only configuration loaded from a local .env file."""
from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", str(BASE_DIR / "amnesia.db")))
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
MIN_CONFLICT_CONFIDENCE = float(os.getenv("MIN_CONFLICT_CONFIDENCE", "0.80"))
if not 0 <= MIN_CONFLICT_CONFIDENCE <= 1:
    raise ValueError("MIN_CONFLICT_CONFIDENCE must be between 0 and 1.")
def telegram_is_configured() -> bool: return bool(TELEGRAM_BOT_TOKEN)

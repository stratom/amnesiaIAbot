"""Fast, repeatable contest demonstration: no Telegram and no API key required."""
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
from database import Database
from agent import AmnesiaAgent
from config import MIN_CONFLICT_CONFIDENCE

# Windows terminals may default to CP-1252, which cannot display the Amnesia emoji.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

with TemporaryDirectory() as tmp:
 db=Database(Path(tmp)/"demo.db"); agent=AmnesiaAgent(db, MIN_CONFLICT_CONFIDENCE)
 first="Queda acordado que todos los FortiGate de producción deben quedar en 7.4.11."
 second="Dejemos el FortiGate de Bajío en 7.4.9."
 one=agent.analyze_message("-100-demo","Demo group","100","demo_user",1,first,"2026-01-01T00:00:00+00:00")
 print("\n=== AMNESIA · OFFLINE CONTEST DEMO ===")
 print("\n1) Telegram group message\n   " + first)
 print("🧠 Amnesia remembered a decision" if one.decision_id else "No important signal detected.")
 two=agent.analyze_message("-100-demo","Demo group","100","demo_user",2,second,"2026-01-01T00:01:00+00:00")
 print("\n2) Telegram group message\n   " + second)
 print("⚠️ Amnesia detected a possible contradiction" if two.conflict_id else "No important signal detected.")
 print("\nDemo complete · local SQLite only · no Telegram or OpenAI required.")

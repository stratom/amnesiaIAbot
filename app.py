"""Telegram polling entry point for Amnesia."""
import logging
from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters
from agent import AmnesiaAgent
from config import DATABASE_PATH, MIN_CONFLICT_CONFIDENCE, TELEGRAM_BOT_TOKEN, telegram_is_configured
from database import Database
from telegram_handlers import amnesia_status, callback, conflicts, decisions, handle_message, help_command

logging.basicConfig(level=logging.INFO,format="%(asctime)s | %(levelname)s | Amnesia | %(message)s")
def main():
    if not telegram_is_configured(): raise SystemExit("Missing TELEGRAM_BOT_TOKEN. Copy .env.example to .env and add your BotFather token.")
    db=Database(DATABASE_PATH); app=Application.builder().token(TELEGRAM_BOT_TOKEN).build(); app.bot_data["agent"]=AmnesiaAgent(db,MIN_CONFLICT_CONFIDENCE)
    app.add_handler(CommandHandler("decisions",decisions)); app.add_handler(CommandHandler("conflicts",conflicts)); app.add_handler(CommandHandler("amnesia",amnesia_status)); app.add_handler(CommandHandler("help",help_command))
    app.add_handler(CallbackQueryHandler(callback)); app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,handle_message))
    logging.info("Starting Telegram polling (minimum conflict confidence: %.0f%%)",MIN_CONFLICT_CONFIDENCE*100); app.run_polling(allowed_updates=Update.ALL_TYPES)
if __name__=="__main__": main()

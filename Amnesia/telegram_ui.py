"""Telegram presentation helpers: concise branded text and inline controls."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
def conflict_keyboard(conflict_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("Create exception",callback_data=f"exception:{conflict_id}"),InlineKeyboardButton("Update decision",callback_data=f"update:{conflict_id}"),InlineKeyboardButton("Ignore",callback_data=f"ignore:{conflict_id}")]])
def conflict_text(previous: str, new_subject: str, new_value: str, confidence: float) -> str:
    return f"⚠️ Amnesia detected a possible contradiction\n\nPrevious decision:\n{previous}\n\nNew message:\n{new_subject} → {new_value}\n\nConfidence:\n{confidence:.0%}"

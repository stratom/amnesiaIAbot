"""Polling handlers. Telegram is the only supported messaging platform."""
from __future__ import annotations
import logging
from telegram import Update
from telegram.ext import ContextTypes
from agent import AmnesiaAgent
from database import Database
from telegram_ui import conflict_keyboard, conflict_text

logger=logging.getLogger("amnesia.telegram")
def context_from_update(update: Update) -> tuple[str,str|None,str,str|None,int,str,str]:
    message=update.effective_message; chat=message.chat; user=update.effective_user
    return str(chat.id),chat.title,str(user.id),user.username,message.message_id,message.text.strip(),message.date.isoformat()
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message=update.effective_message
    if not message or not message.text or not message.text.strip() or (update.effective_user and update.effective_user.is_bot): return
    agent: AmnesiaAgent=context.bot_data["agent"]
    try:
        chat_id,title,user_id,username,message_id,text,timestamp=context_from_update(update)
        result=agent.analyze_message(chat_id,title,user_id,username,message_id,text,timestamp)
        if result.decision_id:
            await message.reply_text("🧠 Amnesia remembered a decision")
        elif result.conflict_id:
            conflict=agent.db.get_conflict(result.conflict_id)
            previous=next(d for d in agent.db.active_decisions(chat_id) if d.id==conflict.decision_id)
            await message.reply_text(conflict_text(previous.summary,conflict.new_subject,conflict.new_value,conflict.confidence),reply_markup=conflict_keyboard(conflict.id))
    except Exception as exc: logger.exception("Could not process Telegram message: %s",exc)
async def decisions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id=str(update.effective_chat.id); agent: AmnesiaAgent=context.bot_data["agent"]; items=agent.db.active_decisions(chat_id)
    await update.effective_message.reply_text("🧠 Active decisions\n"+("\n".join(f"• #{d.id}: {d.summary}" for d in items) or "No active decisions."))
async def conflicts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id=str(update.effective_chat.id); agent: AmnesiaAgent=context.bot_data["agent"]; items=agent.db.open_conflicts(chat_id)
    await update.effective_message.reply_text("⚠️ Open conflicts\n"+("\n".join(f"• #{c.id}: {c.reason}" for c in items) or "No open conflicts."))
async def amnesia_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text("🧠 Amnesia is active. I remember explicit decisions and flag possible contradictions; humans approve every change.")
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text("🧠 Amnesia commands\n/decisions — active decisions\n/conflicts — open conflicts\n/amnesia — agent status\n/help — this help")
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query=update.callback_query; await query.answer(); action,raw=query.data.split(":",1); conflict_id=int(raw); agent: AmnesiaAgent=context.bot_data["agent"]; user=query.from_user
    try:
        if action=="exception": agent.db.create_exception(conflict_id,"Telegram-approved exception",str(user.id),user.username); text="🧠 Amnesia created the exception."
        elif action=="update": agent.db.update_decision(conflict_id,str(user.id),user.username); text="🧠 Amnesia updated the decision."
        else: agent.db.ignore_conflict(conflict_id,str(user.id),user.username); text="🧠 Amnesia ignored the conflict."
        await query.edit_message_reply_markup(reply_markup=None); await query.message.reply_text(text)
    except Exception as exc:
        logger.exception("Callback failed: %s",exc); await query.message.reply_text("Amnesia could not apply that action. Please try again.")

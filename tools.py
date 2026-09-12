"""Database tools exposed to the OpenAI Agents SDK."""
from database import Database
from models import DecisionDraft
def build_tools(db: Database, chat_id: str, message_id: int):
    try: from agents import function_tool
    except ImportError: return []
    @function_tool
    def get_active_decisions() -> list[dict]: return [d.model_dump(mode="json") for d in db.active_decisions(chat_id)]
    @function_tool
    def find_related_decisions(subject: str) -> list[dict]: return [d.model_dump(mode="json") for d in db.related_decisions(chat_id,subject)]
    @function_tool
    def save_decision(summary: str, subject: str, value: str, confidence: float) -> dict: return {"decision_id":db.save_decision(chat_id,None,None,None,message_id,DecisionDraft(summary=summary,subject=subject,value=value,confidence=confidence))}
    @function_tool
    def create_conflict(decision_id: int, new_message: str, new_subject: str, new_value: str, reason: str, confidence: float) -> dict: return {"conflict_id":db.create_conflict(decision_id,chat_id,message_id,new_message,new_subject,new_value,reason,confidence)}
    @function_tool
    def create_exception(conflict_id: int, scope: str) -> dict: db.create_exception(conflict_id,scope,"agent","agent"); return {"ok":True}
    @function_tool
    def update_decision(conflict_id: int) -> dict: return {"decision_id":db.update_decision(conflict_id,"agent","agent")}
    @function_tool
    def ignore_conflict(conflict_id: int) -> dict: db.ignore_conflict(conflict_id,"agent","agent"); return {"ok":True}
    return [get_active_decisions,save_decision,find_related_decisions,create_conflict,create_exception,update_decision,ignore_conflict]

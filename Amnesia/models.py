"""Validated domain objects used by the MVP."""
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field

class DecisionDraft(BaseModel):
    summary: str = Field(min_length=5, max_length=1000)
    subject: str = Field(min_length=2, max_length=300)
    value: str = Field(min_length=1, max_length=300)
    confidence: float = Field(ge=0, le=1)
class ConflictDraft(BaseModel):
    decision_id: int
    new_message: str
    reason: str
    confidence: float = Field(ge=0, le=1)
class Decision(BaseModel):
    id: int; chat_id: str; chat_title: str | None = None; user_id: str | None = None; username: str | None = None; message_id: int
    summary: str; subject: str; value: str; confidence: float
    status: Literal["active", "superseded", "archived"]; created_at: datetime
class Conflict(BaseModel):
    id: int; decision_id: int; chat_id: str; message_id: int
    new_message: str; new_subject: str; new_value: str; reason: str; confidence: float
    status: Literal["open", "ignored", "resolved", "exception_created"]; created_at: datetime

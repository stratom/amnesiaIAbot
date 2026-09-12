"""Amnesia analysis: deterministic local fallback plus OpenAI Agents SDK wiring."""
from __future__ import annotations
from dataclasses import dataclass
import logging, re
from database import Database
from models import DecisionDraft
from prompts import ORG_MIND_INSTRUCTIONS
from tools import build_tools

logger=logging.getLogger("amnesia")
@dataclass
class AnalysisResult:
    decision_id: int | None=None; conflict_id: int | None=None; decision: DecisionDraft | None=None
class AmnesiaAgent:
    def __init__(self, db: Database, min_conflict_confidence: float=.80): self.db=db; self.min_conflict_confidence=min_conflict_confidence
    @staticmethod
    def extract_decision(text: str) -> DecisionDraft | None:
        lower=text.lower()
        if not any(marker in lower for marker in ("queda acordado","acordamos","se decide","decidimos")): return None
        product="FortiGate" if "fortigate" in lower else "Decisión"
        scope="producción" if "producci" in lower else "general"
        version=re.search(r"\b\d+\.\d+(?:\.\d+)?\b",text)
        if not version: return None
        subject=f"Todos los {product} de {scope}" if scope != "general" else product
        return DecisionDraft(summary=f"{subject} → {version.group(0)}",subject=f"{product} {scope}",value=version.group(0),confidence=.95)
    @staticmethod
    def extract_proposal(text: str) -> tuple[str,str,str] | None:
        lower=text.lower()
        if not any(marker in lower for marker in ("dejemos","mejor dejemos","mantengamos","cambiemos")): return None
        if "fortigate" not in lower: return None
        version=re.search(r"\b\d+\.\d+(?:\.\d+)?\b",text)
        if not version: return None
        scope="Bajío" if "bajío" in lower or "bajio" in lower else "grupo"
        return f"FortiGate {scope}", "FortiGate", version.group(0)
    def analyze_message(self, chat_id, chat_title, user_id, username, message_id, text, timestamp) -> AnalysisResult:
        if not self.db.record_message(chat_id,chat_title,user_id,username,message_id,text,timestamp): return AnalysisResult()
        decision=self.extract_decision(text)
        if decision: return AnalysisResult(self.db.save_decision(chat_id,chat_title,user_id,username,message_id,decision),decision=decision)
        proposal=self.extract_proposal(text)
        if proposal:
            label, related_subject, value=proposal
            for previous in self.db.related_decisions(chat_id,related_subject):
                if previous.value != value:
                    confidence=.95
                    if confidence < self.min_conflict_confidence: return AnalysisResult()
                    reason=f"Previous decision is {previous.value}; new message proposes {value}."
                    return AnalysisResult(conflict_id=self.db.create_conflict(previous.id,chat_id,message_id,text,label,value,reason,confidence))
        return AnalysisResult()
    def sdk_agent_for_message(self, chat_id, message_id):
        from agents import Agent
        return Agent(name="Amnesia",instructions=ORG_MIND_INSTRUCTIONS,tools=build_tools(self.db,chat_id,message_id))
    async def analyze_with_openai(self, chat_id, message_id, text):
        from agents import Runner
        return await Runner.run(self.sdk_agent_for_message(chat_id,message_id),f"Analyze Telegram message: {text}")
    async def analyze_with_fallback(self, chat_id, chat_title, user_id, username, message_id, text, timestamp):
        """Optional OpenAI path; a failure always falls back to local SQLite analysis."""
        try:
            return await self.analyze_with_openai(chat_id, message_id, text)
        except Exception as exc:
            logger.warning("OpenAI unavailable; using local fallback: %s", exc)
            return self.analyze_message(chat_id,chat_title,user_id,username,message_id,text,timestamp)

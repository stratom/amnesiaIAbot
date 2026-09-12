"""SQLite persistence for Telegram conversations and auditable human decisions."""
from __future__ import annotations
from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from typing import Any
from models import Conflict, Decision, DecisionDraft

class Database:
    def __init__(self, path: str | Path): self.path = str(path); self.initialize()
    @contextmanager
    def connection(self):
        conn = sqlite3.connect(self.path); conn.row_factory = sqlite3.Row
        try: yield conn; conn.commit()
        except Exception: conn.rollback(); raise
        finally: conn.close()
    @staticmethod
    def now() -> str: return datetime.now(timezone.utc).isoformat()
    def initialize(self):
        with self.connection() as conn: conn.executescript("""
CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, chat_id TEXT NOT NULL, chat_title TEXT, user_id TEXT, username TEXT, message_id INTEGER NOT NULL, text TEXT NOT NULL, timestamp TEXT NOT NULL, UNIQUE(chat_id, message_id));
CREATE TABLE IF NOT EXISTS decisions (id INTEGER PRIMARY KEY, chat_id TEXT NOT NULL, chat_title TEXT, user_id TEXT, username TEXT, message_id INTEGER NOT NULL, summary TEXT NOT NULL, subject TEXT NOT NULL, value TEXT NOT NULL, confidence REAL NOT NULL, status TEXT NOT NULL DEFAULT 'active', created_at TEXT NOT NULL, UNIQUE(chat_id, message_id));
CREATE TABLE IF NOT EXISTS conflicts (id INTEGER PRIMARY KEY, decision_id INTEGER NOT NULL REFERENCES decisions(id), chat_id TEXT NOT NULL, message_id INTEGER NOT NULL, new_message TEXT NOT NULL, new_subject TEXT NOT NULL, new_value TEXT NOT NULL, reason TEXT NOT NULL, confidence REAL NOT NULL, status TEXT NOT NULL DEFAULT 'open', created_at TEXT NOT NULL, UNIQUE(decision_id, chat_id, message_id));
CREATE TABLE IF NOT EXISTS decision_exceptions (id INTEGER PRIMARY KEY, decision_id INTEGER NOT NULL REFERENCES decisions(id), conflict_id INTEGER REFERENCES conflicts(id), scope TEXT NOT NULL, approved_by_user_id TEXT, approved_by_username TEXT, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS agent_actions (id INTEGER PRIMARY KEY, action_type TEXT NOT NULL, entity_type TEXT NOT NULL, entity_id INTEGER, payload TEXT NOT NULL, created_at TEXT NOT NULL);
""")
    def audit(self, action: str, entity: str, entity_id: int | None, payload: dict[str, Any]):
        with self.connection() as conn: conn.execute("INSERT INTO agent_actions(action_type,entity_type,entity_id,payload,created_at) VALUES(?,?,?,?,?)", (action, entity, entity_id, json.dumps(payload, ensure_ascii=False), self.now()))
    def record_message(self, chat_id, chat_title, user_id, username, message_id, text, timestamp) -> bool:
        try:
            with self.connection() as conn: conn.execute("INSERT INTO messages(chat_id,chat_title,user_id,username,message_id,text,timestamp) VALUES(?,?,?,?,?,?,?)", (chat_id, chat_title, user_id, username, message_id, text, timestamp))
            return True
        except sqlite3.IntegrityError: return False
    def save_decision(self, chat_id, chat_title, user_id, username, message_id, draft: DecisionDraft) -> int | None:
        try:
            with self.connection() as conn:
                cur=conn.execute("INSERT INTO decisions(chat_id,chat_title,user_id,username,message_id,summary,subject,value,confidence,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)", (chat_id,chat_title,user_id,username,message_id,draft.summary,draft.subject,draft.value,draft.confidence,self.now()))
                ident=cur.lastrowid
            self.audit("save_decision","decision",ident,draft.model_dump()); return ident
        except sqlite3.IntegrityError: return None
    def active_decisions(self, chat_id: str) -> list[Decision]:
        with self.connection() as conn: rows=conn.execute("SELECT * FROM decisions WHERE chat_id=? AND status='active' ORDER BY id DESC",(chat_id,)).fetchall()
        return [Decision(**dict(row)) for row in rows]
    def related_decisions(self, chat_id: str, subject: str) -> list[Decision]:
        terms=[term for term in subject.lower().split() if len(term)>3]
        return [d for d in self.active_decisions(chat_id) if any(term in (d.subject+" "+d.summary).lower() for term in terms)]
    def create_conflict(self, decision_id, chat_id, message_id, new_message, new_subject, new_value, reason, confidence) -> int | None:
        try:
            with self.connection() as conn:
                cur=conn.execute("INSERT INTO conflicts(decision_id,chat_id,message_id,new_message,new_subject,new_value,reason,confidence,created_at) VALUES(?,?,?,?,?,?,?,?,?)", (decision_id,chat_id,message_id,new_message,new_subject,new_value,reason,confidence,self.now())); ident=cur.lastrowid
            self.audit("create_conflict","conflict",ident,{"decision_id":decision_id,"reason":reason}); return ident
        except sqlite3.IntegrityError: return None
    def open_conflicts(self, chat_id: str) -> list[Conflict]:
        with self.connection() as conn: rows=conn.execute("SELECT * FROM conflicts WHERE chat_id=? AND status='open' ORDER BY id DESC",(chat_id,)).fetchall()
        return [Conflict(**dict(row)) for row in rows]
    def get_conflict(self, conflict_id: int) -> Conflict:
        with self.connection() as conn: row=conn.execute("SELECT * FROM conflicts WHERE id=?",(conflict_id,)).fetchone()
        if not row: raise ValueError("Conflict not found")
        return Conflict(**dict(row))
    def create_exception(self, conflict_id: int, scope: str, user_id: str, username: str | None):
        conflict=self.get_conflict(conflict_id)
        with self.connection() as conn:
            conn.execute("INSERT INTO decision_exceptions(decision_id,conflict_id,scope,approved_by_user_id,approved_by_username,created_at) VALUES(?,?,?,?,?,?)",(conflict.decision_id,conflict_id,scope,user_id,username,self.now()))
            conn.execute("UPDATE conflicts SET status='exception_created' WHERE id=?",(conflict_id,))
        self.audit("create_exception","conflict",conflict_id,{"approved_by":user_id,"scope":scope})
    def update_decision(self, conflict_id: int, user_id: str, username: str | None) -> int:
        """Human approval supersedes the old decision and creates the proposed active one."""
        conflict=self.get_conflict(conflict_id)
        with self.connection() as conn:
            previous=conn.execute("SELECT * FROM decisions WHERE id=?",(conflict.decision_id,)).fetchone()
            if not previous: raise ValueError("Previous decision not found")
            conn.execute("UPDATE decisions SET status='superseded' WHERE id=?",(conflict.decision_id,))
            cur=conn.execute("INSERT INTO decisions(chat_id,chat_title,user_id,username,message_id,summary,subject,value,confidence,status,created_at) VALUES(?,?,?,?,?,?,?,?,?,'active',?)",(previous['chat_id'],previous['chat_title'],user_id,username,conflict.message_id,f"{conflict.new_subject} → {conflict.new_value}",conflict.new_subject,conflict.new_value,conflict.confidence,self.now()))
            new_id=cur.lastrowid; conn.execute("UPDATE conflicts SET status='resolved' WHERE id=?",(conflict_id,))
        self.audit("update_decision","decision",new_id,{"superseded":conflict.decision_id,"approved_by":user_id}); return new_id
    def ignore_conflict(self, conflict_id: int, user_id: str, username: str | None):
        with self.connection() as conn: conn.execute("UPDATE conflicts SET status='ignored' WHERE id=?",(conflict_id,))
        self.audit("ignore_conflict","conflict",conflict_id,{"ignored_by":user_id,"username":username})

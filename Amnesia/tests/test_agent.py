from agent import AmnesiaAgent
from database import Database
def message(agent, ident, text): return agent.analyze_message("-100","Demo", "42","alice",ident,text,f"2026-01-01T00:0{ident}:00+00:00")
def test_decision_and_contradiction(tmp_path):
 agent=AmnesiaAgent(Database(tmp_path/"db.sqlite"))
 decision=message(agent,1,"Queda acordado que todos los FortiGate de producción deben quedar en 7.4.11.")
 conflict=message(agent,2,"Dejemos el FortiGate de Bajío en 7.4.9.")
 assert decision.decision_id and decision.decision.summary=="Todos los FortiGate de producción → 7.4.11"
 assert conflict.conflict_id
def test_duplicate_message_is_ignored(tmp_path):
 agent=AmnesiaAgent(Database(tmp_path/"db.sqlite")); text="Queda acordado que todos los FortiGate de producción deben quedar en 7.4.11."
 assert message(agent,1,text).decision_id
 assert message(agent,1,text).decision_id is None
def test_conflict_threshold(tmp_path):
 agent=AmnesiaAgent(Database(tmp_path/"db.sqlite"),.96)
 message(agent,1,"Queda acordado que todos los FortiGate de producción deben quedar en 7.4.11.")
 assert message(agent,2,"Dejemos el FortiGate de Bajío en 7.4.9.").conflict_id is None

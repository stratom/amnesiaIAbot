from database import Database
from models import DecisionDraft
def decision(): return DecisionDraft(summary="Todos los FortiGate de producción → 7.4.11",subject="FortiGate producción",value="7.4.11",confidence=.95)
def test_update_supersedes_and_creates_active_decision(tmp_path):
 db=Database(tmp_path/"db.sqlite"); old=db.save_decision("chat","Group","1","alice",1,decision())
 conflict=db.create_conflict(old,"chat",2,"Dejemos Bajío en 7.4.9","FortiGate Bajío","7.4.9","different version",.95)
 new=db.update_decision(conflict,"2","bob")
 active=db.active_decisions("chat")
 assert active[0].id==new and active[0].value=="7.4.9"
def test_exception_preserves_original_decision(tmp_path):
 db=Database(tmp_path/"db.sqlite"); old=db.save_decision("chat","Group","1","alice",1,decision())
 conflict=db.create_conflict(old,"chat",2,"new","FortiGate Bajío","7.4.9","different",.95)
 db.create_exception(conflict,"Bajío only","2","bob")
 assert db.active_decisions("chat")[0].id==old
 assert db.get_conflict(conflict).status=="exception_created"

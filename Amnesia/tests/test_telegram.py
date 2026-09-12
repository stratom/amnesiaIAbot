from telegram_ui import conflict_keyboard, conflict_text
def test_telegram_conflict_ui():
 keyboard=conflict_keyboard(5)
 assert [button.text for button in keyboard.inline_keyboard[0]]==["Create exception","Update decision","Ignore"]
 text=conflict_text("Todos los FortiGate de producción → 7.4.11","FortiGate Bajío","7.4.9",.95)
 assert "95%" in text and "Previous decision" in text

# Amnesia — Organizational Intelligence for Telegram

Amnesia is an organizational-intelligence bot for Telegram groups. It remembers explicit decisions in SQLite and alerts the group when a new proposal may contradict an active decision. It is a contest-ready MVP: small, local, easy to run, and free of extra infrastructure.

## What it does

- Reads Telegram group messages through polling; no webhook or public server is required.
- Ignores empty messages and messages sent by bots to prevent loops.
- Prevents duplicate processing with `chat_id + message_id`.
- Stores the chat ID and title, user ID, username, message ID, text, and timestamp.
- Detects explicit decisions, such as:

```text
It is agreed that all production FortiGates must use 7.4.11.
```

- Stores active decisions in SQLite.
- Checks previous decisions from the same Telegram group.
- Detects potential contradictions.
- Presents human-review controls with Telegram `InlineKeyboardMarkup`:
  - Create exception
  - Update decision
  - Ignore
- Audits relevant events in `agent_actions`.
- Uses a deterministic local fallback, so the demo and core logic continue working if OpenAI is unavailable.

## Architecture

```text
Telegram Group
    ↓
Telegram Bot (polling)
    ↓
Amnesia Agent
    ↓
OpenAI Agents SDK / local fallback
    ↓
Tools
    ↓
SQLite
    ↓
Telegram Group
```

## Technology

- Python 3.12+
- OpenAI Agents SDK
- python-telegram-bot
- SQLite
- Pydantic
- python-dotenv
- pytest

Amnesia intentionally does not use webhooks, FastAPI, Redis, Docker, PostgreSQL, Neo4j, LangChain, or LangGraph.

## Project structure

```text
Amnesia/
├── app.py                 # Telegram polling entry point
├── agent.py               # Local analysis and OpenAI Agents SDK wiring
├── tools.py               # SDK function tools for SQLite
├── database.py            # SQLite persistence and audit trail
├── models.py              # Pydantic models
├── config.py              # Environment configuration
├── telegram_handlers.py   # Messages, commands, and callback handlers
├── telegram_ui.py         # Inline keyboard and Telegram message formatting
├── prompts.py             # Agent instructions
├── demo_local.py          # Offline demo without Telegram or OpenAI
├── requirements.txt
├── .env.example
├── .gitignore
├── run_windows.bat
├── run_linux.sh
├── README.md
├── DEMO_SCRIPT.md
└── tests/
```

## Requirements

- Python 3.12 or newer.
- A Telegram account.
- A Telegram bot created with `@BotFather`.
- A Telegram bot token.
- An optional OpenAI API key.
- Internet access for dependency installation and Telegram polling.

## 1. Create the Telegram bot

1. Open Telegram and search for `@BotFather`.
2. Send `/newbot`.
3. Choose a display name, for example `Amnesia`.
4. Choose a unique username ending in `bot`, for example `MyAmnesiaBot`.
5. Copy the token BotFather provides.
6. Send `/setprivacy` to BotFather.
7. Select the Amnesia bot and choose **Disable**. This lets it receive regular group messages.

## 2. Create the group

1. Create a Telegram group, for example `Amnesia Demo`.
2. Add Amnesia to the group.
3. Open group information → **Administrators** → **Add Admin**.
4. Select Amnesia. Basic permissions are sufficient for this MVP; admin access makes the demo setup straightforward.

## 3. Configure environment variables

Create a local configuration file:

```bash
cp .env.example .env
```

Open `.env` and set:

```dotenv
TELEGRAM_BOT_TOKEN=your_botfather_token
OPENAI_API_KEY=your_optional_openai_key
DATABASE_PATH=amnesia.db
MIN_CONFLICT_CONFIDENCE=0.80
```

Never commit `.env`, tokens, API keys, or SQLite database files. They are already excluded by `.gitignore`.

## 4. Run on CachyOS / Linux

CachyOS is Arch Linux based. Install Python first if necessary:

```bash
sudo pacman -Syu --needed python python-pip
cd ~/Amnesia
chmod +x run_linux.sh
./run_linux.sh
```

The launcher creates `.venv`, installs dependencies, and starts Telegram polling.

Manual option:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## 5. Run on Windows

```powershell
cd "C:\path\to\Amnesia"
.\run_windows.bat
```

Manual option:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

## Telegram commands

```text
/decisions   Show active decisions in the current group.
/conflicts   Show open conflicts in the current group.
/amnesia     Show agent status and description.
/help        Show available commands.
```

## Test a decision

Send this message to the group:

```text
Queda acordado que todos los FortiGate de producción deben quedar en 7.4.11.
```

Expected response:

```text
🧠 Amnesia remembered a decision
```

## Test a contradiction

Send this message:

```text
Dejemos el FortiGate de Bajío en 7.4.9.
```

Expected response:

```text
⚠️ Amnesia detected a possible contradiction
```

The alert displays the previous decision, the new proposal, a confidence score, and human-review buttons.

## Human review actions

### Create exception

Keeps the original decision active and records an approved exception, including the Telegram user who approved it.

### Update decision

Marks the previous decision as `superseded`, creates the new decision as `active`, and resolves the conflict.

### Ignore

Marks the conflict as `ignored`.

## Database

Amnesia automatically creates these SQLite tables:

```text
messages
decisions
conflicts
decision_exceptions
agent_actions
```

The default database file is `amnesia.db`.

## Offline demo

The local demo does not need Telegram, an API key, or internet access:

```bash
python demo_local.py
```

It simulates a stored decision followed by a detected contradiction.

## Tests

```bash
python -m pytest -q
python -m compileall .
python demo_local.py
```

The tests cover decision detection, contradiction detection, message deduplication, confidence thresholds, exceptions, superseding decisions, and Telegram UI controls.

## Security

- Never publish Telegram bot tokens or OpenAI API keys.
- Never commit `.env` or SQLite database files.
- Revoke and replace any credential that is exposed.
- Use a higher `MIN_CONFLICT_CONFIDENCE` value to reduce false-positive alerts.

## Project status

Amnesia is a functional MVP for demonstrations and learning. Its local detector deliberately prioritizes clear, explicit decisions and contradictions to avoid spamming Telegram groups.

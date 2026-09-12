# Amnesia — inteligencia organizacional para Telegram

Amnesia es un MVP para grupos de Telegram. Recuerda decisiones explícitas en SQLite y avisa solo cuando una nueva propuesta parece contradecir una decisión activa. Usa **polling**: no necesita webhook, FastAPI, Docker, Redis ni servidores públicos.

```text
Telegram Group → Telegram Bot → Amnesia Agent → OpenAI Agents SDK / Tools → SQLite → Telegram Group
```

El detector local es el fallback: la demo y la operación básica continúan aunque OpenAI no responda. El SDK conserva `Agent`, `Runner` y `function_tool` para el análisis enriquecido.

## Archivos principales

| Archivo | Uso |
|---|---|
| `app.py` | Arranque por polling y registro de handlers. |
| `telegram_handlers.py` | Mensajes, comandos y `CallbackQueryHandler`. |
| `telegram_ui.py` | Mensajes y `InlineKeyboardMarkup`. |
| `agent.py` | Detección local y cableado OpenAI Agents SDK. |
| `database.py` | SQLite: mensajes, decisiones, conflictos, excepciones y auditoría. |
| `demo_local.py` | Demostración sin Telegram ni API key. |

## 1. Instalar Python y dependencias

Instala Python 3.12 desde [python.org](https://www.python.org/downloads/). En Windows marca **Add Python to PATH**. En Linux instala `python3.12`, `python3.12-venv` y `pip` usando el gestor de paquetes de tu distribución.

En la carpeta del proyecto:

```powershell
cd "C:\Users\ALDO MONTES DE OCA\Downloads\neo\STAP\Amnesia"
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

En Linux genérico:

```bash
cd /ruta/a/Amnesia
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

`run_windows.bat` crea el entorno e instala dependencias automáticamente en Windows.

### CachyOS

CachyOS está basado en Arch Linux. Actualiza el sistema e instala Python si aún no está disponible:

```bash
sudo pacman -Syu python python-pip
cd /ruta/a/Amnesia
chmod +x run_linux.sh
./run_linux.sh
```

El lanzador crea `.venv`, instala las dependencias y arranca el polling de Telegram. Python 3.12 o superior es compatible.

## 2. Crear el bot con BotFather

1. Abre Telegram y busca **@BotFather**. Verifica que sea el bot oficial.
2. Pulsa **Start** y envía `/newbot`.
3. Escribe el nombre `Amnesia` y un username único que termine en `bot`, por ejemplo `MiAmnesiaBot`.
4. BotFather entregará un token. Cópialo y mantenlo privado.
5. Envía `/setprivacy`, elige Amnesia y selecciona **Disable**. Así podrá leer mensajes normales dentro de grupos.

## 3. Crear el grupo y agregar Amnesia

1. En Telegram crea un grupo nuevo, por ejemplo `Amnesia Demo`.
2. Abre la información del grupo → **Add members** → busca tu bot Amnesia y agrégalo.
3. Ve a **Administrators** → **Add Admin** → selecciona Amnesia. Para este MVP basta con permisos básicos; hacerlo administrador simplifica la demostración y confirma que puede operar en el grupo.

## 4. Configurar `.env`

Abre `.env` y completa:

```dotenv
TELEGRAM_BOT_TOKEN=pega_el_token_de_BotFather
OPENAI_API_KEY=tu_clave_openai_opcional
DATABASE_PATH=amnesia.db
MIN_CONFLICT_CONFIDENCE=0.80
```

No compartas este archivo. Está ignorado por Git. `OPENAI_API_KEY` es opcional para el fallback local; Telegram necesita `TELEGRAM_BOT_TOKEN`.

## 5. Ejecutar Amnesia

Con el entorno activado:

```powershell
python app.py
```

El proceso inicia polling. Déjalo abierto mientras hagas la demo. No hay webhook que configurar.

## 6. Probar decisiones y contradicciones

Envía al grupo:

```text
Queda acordado que todos los FortiGate de producción deben quedar en 7.4.11.
```

Amnesia responde `🧠 Amnesia remembered a decision`. Luego envía:

```text
Dejemos el FortiGate de Bajío en 7.4.9.
```

Amnesia mostrará una tarjeta de contradicción con la decisión previa, la propuesta nueva y confianza de 95%.

### Botones

- **Create exception:** conserva la decisión original y registra la excepción con el usuario aprobador.
- **Update decision:** marca la decisión previa como `superseded`, crea la nueva como `active` y resuelve el conflicto.
- **Ignore:** marca el conflicto como `ignored`.

## Comandos

```text
/decisions   Decisiones activas del grupo actual
/conflicts   Conflictos abiertos del grupo actual
/amnesia     Estado y descripción del agente
/help        Lista de comandos
```

## Demo local y pruebas

No requiere token ni Telegram:

```powershell
python demo_local.py
python -m pytest -q
python -m compileall .
```

Las pruebas cubren decisión, contradicción, deduplicación por `chat_id + message_id`, umbral de confianza, excepción, actualización `superseded → active` y la interfaz Telegram.

## Tablas SQLite

`messages` guarda `chat_id`, título, usuario, username, `message_id`, texto y timestamp. Las otras tablas son `decisions`, `conflicts`, `decision_exceptions` y `agent_actions`. La combinación `chat_id + message_id` evita duplicados.

## Problemas comunes

- **El bot no ve mensajes del grupo:** vuelve a ejecutar `/setprivacy` en BotFather y elige **Disable**; retira y vuelve a agregar el bot si es necesario.
- **`Missing TELEGRAM_BOT_TOKEN`:** crea `.env` desde `.env.example` y agrega el token de BotFather.
- **El bot responde a otro bot:** Amnesia ignora mensajes cuyo remitente es bot para evitar loops.
- **No hay alerta:** mensajes casuales, vacíos, duplicados o por debajo de `MIN_CONFLICT_CONFIDENCE` se ignoran deliberadamente.

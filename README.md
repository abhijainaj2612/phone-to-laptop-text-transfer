# Phone PC Type Assistant

Send text from Android Chrome to a Windows PC across completely different networks, then type it into the active Windows app. The PC makes an **outbound** secure WebSocket connection to the relay—there is no port forwarding, public PC address, or inbound PC server.

```
Android browser ── HTTPS ──> Relay server ── WSS ──> Windows PC client ──> Active app
```

The relay forwards text in memory only. It does not write message contents to a database or log them.

## What is included

- `relay_server/` — FastAPI HTTPS/WebSocket relay, signed phone tokens, expiring six-digit pairing codes, rate limits and message limits.
- `pc_client/` — Windows outbound WebSocket client, global hotkeys and randomized typing engine.
- `phone_web/` — mobile-first browser interface served by the relay.
- `tests/` — unit tests; they mock the typing libraries and never type into real applications.

## 1. Deploy the relay

You need a small Python host that provides HTTPS and supports WebSockets (for example Render, Railway, Fly.io, or a VPS behind Caddy/nginx). Create a service from this folder and set these environment variables in its dashboard:

```text
SECRET_KEY=<generate a unique long random secret>
PAIRING_CODE_EXPIRY=300
MAX_MESSAGE_SIZE=50000
RATE_LIMIT=30
```

Generate `SECRET_KEY` on a trusted computer:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Install command:

```text
pip install -r requirements-relay.txt
```

Start command (the platform should terminate TLS and supply the public HTTPS URL):

```text
uvicorn relay_server.main:app --host 0.0.0.0 --port $PORT
```

For local-only development, create a `.env` from `.env.example`, set `SECRET_KEY`, and use `uvicorn relay_server.main:app --reload`. A phone on another network still needs the deployed HTTPS service; never expose a Windows PC port for this project.

## 2. Set up the Windows PC

Install Python 3.10 or later from [python.org](https://www.python.org/downloads/windows/) and check **Add Python to PATH**. In PowerShell, inside this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-pc.txt
Copy-Item .env.example .env
notepad .env
```

In `.env`, set only the PC values:

```text
RELAY_URL=https://your-relay-domain.example
TYPING_SPEED=normal
```

Keep `SECRET_KEY` only on the relay host; it does not belong in the PC `.env`. Start the client:

```powershell
.\.venv\Scripts\python.exe -m pc_client.main
```

Or double-click `run_pc.bat` after installing dependencies with the same Python. The first run stores a random PC identity/token in `%USERPROFILE%\.phone_pc_type_assistant.json`; keep that file private. Leave the terminal running. It prints an expiring pairing code.

### Run silently in the background

After the first successful pairing, double-click `start_background.vbs`. It starts the PC client through `pythonw.exe`, so no PowerShell or terminal must stay open.

To start it automatically whenever you sign into Windows, double-click `install_startup.vbs` once. To undo that, double-click `remove_startup.vbs`. Do not start it both manually and through startup at the same time; use one running client instance.

## 3. Pair the Android phone

1. In Android Chrome, open the public `https://your-relay-domain.example`.
2. Enter the six-digit code currently shown by the PC client.
3. The page reports `PC Connected` when the outbound PC connection is live.
4. The phone keeps a signed token in its browser local storage, so normally this is a one-time step.

To revoke that browser, use **Disconnect this phone** (which removes its local token). For a stronger reset, stop the PC client and delete `%USERPROFILE%\.phone_pc_type_assistant.json`, then restart it; this creates a new PC identity and pairing code. Re-deploying with a new `SECRET_KEY` invalidates all phone sessions.

## 4. Send and type text

1. Paste/type into the phone text field and select **Send to PC**.
2. On Windows, open the target app and click exactly where text should be inserted.
3. Press `Ctrl` + `Shift` + `T`.
4. The client counts down three seconds without stealing focus, then types the saved message.
5. Press `Esc` at any time to stop as quickly as the current keystroke permits.

Only one typing operation can run at once. New messages received during typing remain queued as the latest text and do not replace the in-progress operation.

## Security and privacy notes

- Production requires HTTPS/WSS; do not use plain HTTP for real use.
- Pairing codes expire (five minutes by default); tokens are HMAC-signed and a browser can send only to its paired PC identity.
- Messages are constrained by size and simple per-IP/per-device rate limits.
- Full message text is neither logged nor retained by the relay. The PC keeps only the latest text in RAM.
- No analytics, accounts, database, direct LAN addressing, or inbound PC ports are used.

## Known limitations

- A single relay process keeps live PC connections in memory. Running multiple relay replicas needs shared routing and is intentionally out of scope.
- Browser session tokens survive a relay restart only if `SECRET_KEY` remains unchanged; the PC reconnects automatically.
- ASCII is typed character-by-character with natural timing. Non-ASCII runs use temporary clipboard paste and restore **text** clipboard contents afterward. Rich clipboard formats may not be restored, and highly locked-down apps can block simulated input.
- Windows may show a permissions/accessibility prompt for global keyboard listening. Some elevated applications do not accept input from a non-elevated client; start the client at the same privilege level only when necessary.

## Test and lint sanity checks

```powershell
python -m compileall pc_client relay_server
pip install pytest pytest-asyncio
python -m pytest -q
```

import asyncio
import logging
import secrets
from datetime import datetime, timezone
from pathlib import Path
from fastapi import Depends, FastAPI, Header, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .auth import RateLimiter, issue_phone_token, verify_phone_token
from .config import Settings
from .connection_manager import ConnectionManager
from .models import PairRequest, TextRequest

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
settings = Settings(); settings.validate()
manager = ConnectionManager(settings.pairing_code_expiry)
limiter = RateLimiter(settings.rate_limit)
app = FastAPI(title="Phone PC Type Assistant")
origins = [item.strip() for item in settings.allowed_origins.split(",") if item.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False,
                   allow_methods=["GET", "POST"], allow_headers=["Authorization", "Content-Type"])
WEB_ROOT = Path(__file__).resolve().parent.parent / "phone_web"
app.mount("/static", StaticFiles(directory=WEB_ROOT), name="static")

def client_key(request: Request) -> str:
    return request.client.host if request.client else "unknown"

def phone_device(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing phone token")
    device_id = verify_phone_token(authorization[7:], settings.secret_key)
    if not device_id:
        raise HTTPException(401, "Invalid phone token")
    return device_id

@app.get("/")
async def index(): return FileResponse(WEB_ROOT / "index.html")

@app.get("/style.css")
async def stylesheet(): return FileResponse(WEB_ROOT / "style.css", media_type="text/css")

@app.get("/app.js")
async def application_script(): return FileResponse(WEB_ROOT / "app.js", media_type="application/javascript")

@app.get("/config.js")
async def configuration_script(): return FileResponse(WEB_ROOT / "config.js", media_type="application/javascript")

@app.post("/api/pair")
async def pair(body: PairRequest, request: Request):
    if not limiter.allowed("pair:" + client_key(request)):
        raise HTTPException(429, "Too many pairing attempts")
    device_id = manager.pair(body.code)
    if not device_id:
        raise HTTPException(400, "Invalid, expired, or already used pairing code")
    logging.info("Phone paired with device %s", device_id[:8])
    return {"device_id": device_id, "token": issue_phone_token(device_id, settings.secret_key)}

@app.get("/api/status")
async def status(device_id: str = Depends(phone_device)):
    return {"pc_online": manager.online(device_id)}

@app.post("/api/message")
async def message(body: TextRequest, request: Request, device_id: str = Depends(phone_device)):
    if len(body.text) > settings.max_message_size:
        raise HTTPException(413, "Text is too large")
    if not limiter.allowed("message:" + device_id):
        raise HTTPException(429, "Too many messages; try again shortly")
    message_id = secrets.token_urlsafe(12)
    delivered = await manager.send_text(device_id, {"type": "text_received", "message_id": message_id,
        "text": body.text, "timestamp": datetime.now(timezone.utc).isoformat()})
    if not delivered:
        raise HTTPException(503, "PC is currently offline")
    logging.info("Forwarded message %s (%d characters)", message_id, len(body.text))
    return {"message_id": message_id, "status": "delivered"}

@app.websocket("/ws/pc")
async def pc_socket(websocket: WebSocket):
    await websocket.accept()
    device_id = websocket.query_params.get("device_id", "")
    token = websocket.query_params.get("token", "")
    if not device_id or not token:
        await websocket.close(code=1008); return
    try:
        code = await manager.connect_pc(device_id, token, websocket)
    except PermissionError:
        await websocket.close(code=1008); return
    await websocket.send_json({"type": "registered", "pairing_code": code, "expires_in": settings.pairing_code_expiry})
    logging.info("PC connected: %s", device_id[:8])
    try:
        while True:
            await websocket.receive_json()  # ACKs are deliberately not persisted
    except (WebSocketDisconnect, ValueError):
        await manager.disconnect_pc(device_id, websocket)
        logging.info("PC disconnected: %s", device_id[:8])

import json
import os
import secrets
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

STATE_FILE = Path.home() / ".phone_pc_type_assistant.json"
load_dotenv()

@dataclass
class PCConfig:
    relay_url: str
    device_id: str
    device_token: str
    typing_speed: str

    @classmethod
    def load(cls):
        saved = json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}
        relay = os.getenv("RELAY_URL", saved.get("relay_url", ""))
        if not relay: raise RuntimeError("Set RELAY_URL in .env or your environment")
        config = cls(relay.rstrip("/"), saved.get("device_id", secrets.token_urlsafe(12)),
                     saved.get("device_token", secrets.token_urlsafe(32)), os.getenv("TYPING_SPEED", "normal"))
        STATE_FILE.write_text(json.dumps(config.__dict__, indent=2))
        return config

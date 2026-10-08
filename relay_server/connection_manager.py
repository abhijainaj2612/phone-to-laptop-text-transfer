import asyncio
import time
from dataclasses import dataclass
from fastapi import WebSocket
from .auth import new_code


@dataclass
class Device:
    websocket: WebSocket
    token: str
    pairing_code: str
    code_expires_at: float


class ConnectionManager:
    def __init__(self, code_expiry: int):
        self.code_expiry = code_expiry
        self.devices: dict[str, Device] = {}
        self._lock = asyncio.Lock()

    async def connect_pc(self, device_id: str, token: str, websocket: WebSocket) -> str:
        async with self._lock:
            old = self.devices.get(device_id)
            if old and old.token != token:
                raise PermissionError("device token mismatch")
            code = new_code()
            self.devices[device_id] = Device(websocket, token, code, time.monotonic() + self.code_expiry)
            return code

    async def disconnect_pc(self, device_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            if self.devices.get(device_id) and self.devices[device_id].websocket is websocket:
                self.devices.pop(device_id, None)

    def pair(self, code: str) -> str | None:
        now = time.monotonic()
        for device_id, device in list(self.devices.items()):
            if device.pairing_code == code and now <= device.code_expires_at:
                # The displayed code is time-limited; this lets a second trusted
                # phone pair during the same short window without a PC restart.
                return device_id
        return None

    def online(self, device_id: str) -> bool:
        return device_id in self.devices

    async def send_text(self, device_id: str, payload: dict) -> bool:
        device = self.devices.get(device_id)
        if not device:
            return False
        try:
            await device.websocket.send_json(payload)
            return True
        except Exception:
            return False

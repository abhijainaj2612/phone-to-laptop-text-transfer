import asyncio
import json
import logging
from urllib.parse import urlencode
import websockets

class RelayClient:
    def __init__(self, config, on_text, on_registered, on_status):
        self.config, self.on_text, self.on_registered, self.on_status = config, on_text, on_registered, on_status

    async def run(self):
        delay = 1
        scheme = "wss" if self.config.relay_url.startswith("https://") else "ws"
        base = self.config.relay_url.split("://", 1)[-1]
        url = f"{scheme}://{base}/ws/pc?" + urlencode({"device_id": self.config.device_id, "token": self.config.device_token})
        while True:
            try:
                self.on_status("Connected")
                async with websockets.connect(url, max_size=100_000, ping_interval=20) as ws:
                    delay = 1
                    async for raw in ws:
                        data = json.loads(raw)
                        if data["type"] == "registered": self.on_registered(data)
                        elif data["type"] == "text_received":
                            self.on_text(data)
                            await ws.send(json.dumps({"type":"ack", "message_id": data["message_id"], "status":"received"}))
            except Exception as exc:
                logging.warning("Relay disconnected: %s; retrying in %ss", type(exc).__name__, delay)
                self.on_status("Disconnected")
                await asyncio.sleep(delay); delay = min(delay * 2, 30)

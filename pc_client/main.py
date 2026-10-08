import asyncio
import logging
import threading
from .config import PCConfig
from .hotkeys import start_hotkeys
from .relay_client import RelayClient
from .typing_engine import TypingEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
class App:
    def __init__(self): self.latest_text=""; self.latest_message_id=""; self.last_typed_text=""; self.engine=None
    def received(self, msg):
        self.latest_text, self.latest_message_id = msg["text"], msg["message_id"]
        logging.info("Text received: %d characters", len(self.latest_text)); print(f"\n✓ Text received ({len(self.latest_text)} characters). Ready to type.")
    def registered(self, msg): print(f"\nPairing code: {msg['pairing_code']} (expires in {msg['expires_in']} seconds)")
    def status(self, value): print(f"Relay: {value}")
    def type_now(self):
        if not self.latest_text: print("No text received yet."); return
        if self.engine and self.engine.running: print("Typing is already running."); return
        text = self.latest_text
        def work():
            for seconds in (3,2,1):
                print(f"Starting in {seconds}...")
                # Event.wait keeps ESC responsive throughout the countdown.
                if self.engine.stop_event.wait(1): return
            result = self.engine.type_text(text)
            if result.completed: self.last_typed_text = text; print("Typing completed.")
            else: print(result.error)
        self.engine.stop_event.clear(); threading.Thread(target=work, daemon=True).start()
    def stop(self):
        if self.engine: self.engine.stop(); print("Typing stopped.")

def main():
    config, app = PCConfig.load(), App(); app.engine = TypingEngine(config.typing_speed)
    print("\nPC TYPE ASSISTANT\n" + "="*36 + f"\nPhone URL: {config.relay_url}\nWaiting for relay...\nCtrl + Shift + T → Type\nESC → Stop")
    start_hotkeys(app.type_now, app.stop)
    asyncio.run(RelayClient(config, app.received, app.registered, app.status).run())
if __name__ == "__main__": main()

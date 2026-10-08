import random
import threading
import time
from dataclasses import dataclass
import pyautogui
import pyperclip

PRESETS = {"fast": (0.01, 0.04), "normal": (0.03, 0.12), "slow": (0.10, 0.25)}

@dataclass
class TypingResult:
    completed: bool
    error: str | None = None

class TypingEngine:
    def __init__(self, speed="normal"):
        self.stop_event = threading.Event(); self._lock = threading.Lock(); self.running = False
        self.min_delay, self.max_delay = PRESETS.get(speed.lower(), PRESETS["normal"])

    def stop(self): self.stop_event.set()

    def _wait(self, seconds):
        return not self.stop_event.wait(seconds)

    @staticmethod
    def _ascii(char): return char in "\n\t" or (32 <= ord(char) <= 126)

    def _paste_unicode(self, text):
        old = pyperclip.paste()
        try:
            pyperclip.copy(text); pyautogui.hotkey("ctrl", "v")
        finally:
            try: pyperclip.copy(old)
            except Exception: pass

    def type_text(self, text: str) -> TypingResult:
        with self._lock:
            if self.running: return TypingResult(False, "Typing is already running")
            self.running = True; self.stop_event.clear()
        try:
            index = 0
            while index < len(text):
                if self.stop_event.is_set(): return TypingResult(False, "Typing stopped")
                char = text[index]
                if not self._ascii(char):
                    end = index + 1
                    while end < len(text) and not self._ascii(text[end]): end += 1
                    self._paste_unicode(text[index:end]); index = end; continue
                if char == "\n": pyautogui.press("enter")
                elif char == "\t": pyautogui.press("tab")
                else: pyautogui.write(char)
                extra = random.uniform(self.min_delay, self.max_delay)
                if char.isspace(): extra += random.uniform(0.05, 0.20)
                elif char in ".!?": extra += random.uniform(0.20, 0.50)
                if not self._wait(extra): return TypingResult(False, "Typing stopped")
                index += 1
            return TypingResult(True)
        except Exception as exc:
            return TypingResult(False, f"Typing failed: {exc}")
        finally:
            with self._lock: self.running = False

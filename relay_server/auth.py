import hashlib
import hmac
import secrets
import time
from collections import defaultdict, deque
from base64 import urlsafe_b64encode, urlsafe_b64decode


def new_token() -> str:
    return secrets.token_urlsafe(32)


def new_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def _sign(payload: bytes, secret: str) -> str:
    return urlsafe_b64encode(hmac.new(secret.encode(), payload, hashlib.sha256).digest()).decode().rstrip("=")


def issue_phone_token(device_id: str, secret: str) -> str:
    payload = f"{device_id}:{int(time.time())}".encode()
    return urlsafe_b64encode(payload).decode().rstrip("=") + "." + _sign(payload, secret)


def verify_phone_token(token: str, secret: str) -> str | None:
    try:
        encoded, signature = token.split(".", 1)
        payload = urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
        if not hmac.compare_digest(_sign(payload, secret), signature):
            return None
        return payload.decode().split(":", 1)[0]
    except (ValueError, UnicodeDecodeError):
        return None


class RateLimiter:
    def __init__(self, limit: int, window_seconds: int = 60):
        self.limit, self.window = limit, window_seconds
        self.requests: dict[str, deque[float]] = defaultdict(deque)

    def allowed(self, key: str) -> bool:
        now, entries = time.monotonic(), self.requests[key]
        while entries and now - entries[0] > self.window:
            entries.popleft()
        if len(entries) >= self.limit:
            return False
        entries.append(now)
        return True

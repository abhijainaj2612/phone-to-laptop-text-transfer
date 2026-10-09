from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    secret_key: str = os.getenv("SECRET_KEY", "")
    pairing_code_expiry: int = int(os.getenv("PAIRING_CODE_EXPIRY", "86400"))
    max_message_size: int = int(os.getenv("MAX_MESSAGE_SIZE", "50000"))
    rate_limit: int = int(os.getenv("RATE_LIMIT", "30"))
    allowed_origins: str = os.getenv("ALLOWED_ORIGINS", "*")

    def validate(self) -> None:
        if not self.secret_key or len(self.secret_key) < 32:
            raise RuntimeError("SECRET_KEY must be a unique value of at least 32 characters")

import base64
import hashlib

from cryptography.fernet import Fernet

from app.core.config import get_settings


def _fernet_key() -> bytes:
    settings = get_settings()
    raw_key = settings.llm_config_encryption_key or settings.jwt_secret_key
    try:
        decoded = base64.urlsafe_b64decode(raw_key.encode())
        if len(decoded) == 32:
            return raw_key.encode()
    except Exception:
        pass
    digest = hashlib.sha256(raw_key.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_secret(secret: str) -> str:
    return Fernet(_fernet_key()).encrypt(secret.encode("utf-8")).decode("utf-8")


def decrypt_secret(encrypted_secret: str | None) -> str | None:
    if not encrypted_secret:
        return None
    return Fernet(_fernet_key()).decrypt(encrypted_secret.encode("utf-8")).decode("utf-8")

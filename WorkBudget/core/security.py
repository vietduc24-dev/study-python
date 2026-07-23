"""Security helpers."""

import base64
import hashlib
import hmac
import secrets

PASSWORD_HASH_ITERATIONS = 390_000


def generate_token(num_bytes: int = 32) -> str:
    """Return a URL-safe random token."""
    return secrets.token_urlsafe(num_bytes)


def hash_token(token: str) -> str:
    """Hash a token for database lookup/storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    """Hash a password with PBKDF2-HMAC-SHA256."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_HASH_ITERATIONS,
    )
    return (
        f"pbkdf2_sha256${PASSWORD_HASH_ITERATIONS}$"
        f"{base64.b64encode(salt).decode()}$"
        f"{base64.b64encode(digest).decode()}"
    )


def verify_password(password: str, password_hash: str | None) -> bool:
    """Verify a password against a stored PBKDF2 hash."""
    if not password_hash:
        return False

    try:
        algorithm, iterations_text, salt_text, digest_text = password_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        iterations = int(iterations_text)
        salt = base64.b64decode(salt_text)
        expected_digest = base64.b64decode(digest_text)
    except (ValueError, TypeError):
        return False

    actual_digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations,
    )
    return hmac.compare_digest(actual_digest, expected_digest)

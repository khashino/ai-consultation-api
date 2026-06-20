import base64
import hashlib
import hmac
import secrets
import time
from typing import Optional

from fastapi import HTTPException, Request, status

from app.core.config import settings


SESSION_MAX_AGE_SECONDS = 60 * 60 * 8
SESSION_VERSION = "v1"


def verify_admin_credentials(username: str, password: str) -> bool:
    valid_username = secrets.compare_digest(
        username,
        settings.admin_username,
    )

    valid_password = secrets.compare_digest(
        password,
        settings.admin_password,
    )

    return valid_username and valid_password


def _sign_payload(payload: str) -> str:
    signature = hmac.new(
        settings.admin_session_secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return signature


def create_admin_session_token(username: str) -> str:
    issued_at = str(int(time.time()))

    payload = f"{SESSION_VERSION}:{username}:{issued_at}"
    signature = _sign_payload(payload)

    raw_token = f"{payload}:{signature}"

    return base64.urlsafe_b64encode(
        raw_token.encode("utf-8")
    ).decode("utf-8")


def parse_admin_session_token(token: str) -> Optional[str]:
    try:
        raw_token = base64.urlsafe_b64decode(
            token.encode("utf-8")
        ).decode("utf-8")

        parts = raw_token.split(":")

        if len(parts) != 4:
            return None

        version, username, issued_at_text, signature = parts

        if version != SESSION_VERSION:
            return None

        payload = f"{version}:{username}:{issued_at_text}"
        expected_signature = _sign_payload(payload)

        if not secrets.compare_digest(signature, expected_signature):
            return None

        issued_at = int(issued_at_text)
        now = int(time.time())

        if now - issued_at > SESSION_MAX_AGE_SECONDS:
            return None

        if not secrets.compare_digest(username, settings.admin_username):
            return None

        return username

    except Exception:
        return None


def get_admin_username_from_request(request: Request) -> Optional[str]:
    token = request.cookies.get(settings.admin_cookie_name)

    if not token:
        return None

    return parse_admin_session_token(token)


def require_admin(request: Request) -> str:
    username = get_admin_username_from_request(request)

    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin login required.",
        )

    return username
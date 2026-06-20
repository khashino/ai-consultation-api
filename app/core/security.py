import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.core.config import settings


security = HTTPBasic()


def require_admin(
    credentials: HTTPBasicCredentials = Depends(security),
) -> str:
    """
    Simple HTTP Basic authentication for admin-only routes.

    Returns the authenticated username if credentials are valid.
    Raises 401 if credentials are invalid.
    """

    valid_username = secrets.compare_digest(
        credentials.username,
        settings.admin_username,
    )

    valid_password = secrets.compare_digest(
        credentials.password,
        settings.admin_password,
    )

    if not valid_username or not valid_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username
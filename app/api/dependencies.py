from types import SimpleNamespace

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config.settings import settings
from app.container import Container, build_container

bearer_scheme = HTTPBearer()


def get_container() -> Container:
    return build_container()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> SimpleNamespace:
    """Delegates token verification to add-ai-auth-service over HTTP —
    this repo holds no JWT secret and never decodes a token itself.
    Returns a SimpleNamespace(id, name, email) so every router below,
    copied from the monolith unchanged, keeps working with `.id` access."""
    try:
        r = httpx.post(
            f"{settings.auth_service_url}/verify",
            json={"token": credentials.credentials},
            timeout=10,
        )
    except httpx.HTTPError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Auth service unreachable")

    if r.status_code != 200:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    return SimpleNamespace(**r.json())

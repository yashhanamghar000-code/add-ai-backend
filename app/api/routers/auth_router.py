"""
The frontend's API contract (`/api/auth/register`, `/login`, `/me`,
`/logout`) doesn't change at all — this router just forwards to
add-ai-auth-service instead of calling an in-process AuthService. That's
the payoff of the frontend depending on a stable HTTP contract rather
than backend internals.
"""
import logging
from types import SimpleNamespace

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request

from app.api.dependencies import get_container, get_current_user
from app.api.schemas.auth_schemas import LoginRequest, RegisterRequest, TokenResponse, UserOut
from app.config.settings import settings
from app.container import Container

logger = logging.getLogger("audito.auth")

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, background_tasks: BackgroundTasks, container: Container = Depends(get_container)):
    r = httpx.post(f"{settings.auth_service_url}/register", json=payload.model_dump(), timeout=15)
    if r.status_code == 400:
        raise HTTPException(status_code=400, detail=r.json().get("detail", "Registration failed"))
    r.raise_for_status()
    body = r.json()
    user = UserOut(id=body["user_id"], name=body["name"], email=body["email"])

    logger.info("New registration -> id=%s name=%r email=%s", user.id, user.name, user.email)

    # Runs after the response is sent. NotificationService itself skips
    # silently if the email verifies as dummy/test, so this is always
    # safe to fire for every registration.
    background_tasks.add_task(container.notification_service.notify_signup, user.name, user.email)

    return TokenResponse(token=body["token"], user=user)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, background_tasks: BackgroundTasks, container: Container = Depends(get_container)):
    r = httpx.post(f"{settings.auth_service_url}/login", json=payload.model_dump(), timeout=15)
    if r.status_code == 401:
        raise HTTPException(status_code=401, detail=r.json().get("detail", "Invalid email or password"))
    r.raise_for_status()
    body = r.json()
    user = UserOut(id=body["user_id"], name=body["name"], email=body["email"])

    device_info = request.headers.get("user-agent", "a device we don't recognize")

    logger.info(
        "Login -> id=%s name=%r email=%s ip=%s device=%s",
        user.id, user.name, user.email,
        request.client.host if request.client else "unknown",
        device_info,
    )

    background_tasks.add_task(container.notification_service.notify_login, user.name, user.email, device_info)

    return TokenResponse(token=body["token"], user=user)


@router.get("/me", response_model=UserOut)
def me(current_user: SimpleNamespace = Depends(get_current_user)):
    return UserOut(id=current_user.id, name=current_user.name, email=current_user.email)


@router.post("/logout")
def logout():
    # Stateless JWT: nothing to invalidate server-side without a
    # blocklist. The frontend just deletes the token from local storage.
    return {"status": "ok"}

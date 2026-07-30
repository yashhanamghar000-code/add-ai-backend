from types import SimpleNamespace

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_container, get_current_user
from app.container import Container

router = APIRouter(prefix="/api", tags=["session"])


@router.delete("/session/{session_id}")
async def clear_session(
    session_id: str,
    container: Container = Depends(get_container),
    current_user: SimpleNamespace = Depends(get_current_user),
):
    user_id = str(current_user.id)
    try:
        container.session_service.clear_session(user_id, session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "success", "detail": f"Session {session_id} cleared for user {user_id}."}

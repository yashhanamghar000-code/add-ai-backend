import traceback
from types import SimpleNamespace

from fastapi import APIRouter, Depends, Form, HTTPException

from app.api.dependencies import get_container, get_current_user
from app.container import Container

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat")
async def secure_chat(
    query: str = Form(...),
    session_id: str = Form(...),
    file_ids: str = Form(None),
    container: Container = Depends(get_container),
    current_user: SimpleNamespace = Depends(get_current_user),
):
    user_id = str(current_user.id)
    try:
        selected_file_ids = [f.strip() for f in file_ids.split(",") if f.strip()] if file_ids else []

        answer = container.chat_workflow_service.run(
            query=query,
            user_id=user_id,
            session_id=session_id,
            selected_file_ids=selected_file_ids,
        )

        container.history_service.save_chat_turn(current_user.id, session_id, query, answer.response_text)
        return answer.to_dict()

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"LLM Orchestration Error: {str(e)}")

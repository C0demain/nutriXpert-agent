from fastapi import APIRouter, HTTPException, Request
from typing import Optional
from nutrixpert.core.models import SessionListItem

router = APIRouter()


@router.get("/{user_id}/list", response_model=list[SessionListItem])
async def list_user_sessions(user_id: str, request: Request, app_name: Optional[str] = None):
    """
    Lista todas as sessões de um usuário.
    Retorna o id da sessão e a primeira mensagem enviada pelo usuário.
    """
    session_service = request.app.state.session_service
    app_name = app_name or request.app.state.app_name

    try:
        sessions_resp = await session_service.list_sessions(app_name=app_name, user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar sessões: {e}")

    sessions = getattr(sessions_resp, "sessions", None) or []
    if not sessions:
        raise HTTPException(status_code=404, detail="Nenhuma sessão encontrada para este usuário")

    output = []
    for s in sessions:
        state = getattr(s, "state", {}) or {}
        messages = state.get("messages", [])

        first_user_msg = None
        for m in messages:
            if m.get("author") == "user":
                first_user_msg = m.get("text", "").strip()
                break

        output.append(SessionListItem(
            session_id=getattr(s, "id", None),
            first_message=first_user_msg
        ))

    return output

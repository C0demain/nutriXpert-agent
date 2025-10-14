from fastapi import APIRouter, Request, HTTPException
from typing import Optional
from nutrixpert.agent import AGENT_OUTPUT_KEY
from nutrixpert.core.schemas.session_list_item import SessionListItem
from nutrixpert.core.schemas.session_message import SessionMessage
from nutrixpert.core.schemas.session_info_response import SessionInfoResponse

router = APIRouter()

@router.get("/sessions/{user_id}/{session_id}", response_model=SessionInfoResponse)
async def get_session_history(user_id: str, session_id: str, request: Request, app_name: Optional[str] = None):
    """
    Recupera o histórico completo de mensagens de uma sessão específica do agente.

    Esta rota consulta o `SessionService` do Google ADK para obter o estado atual da sessão
    de um determinado usuário (`user_id`) dentro de um aplicativo (`app_name`).

    O retorno inclui todas as mensagens trocadas (usuário ↔ agente), além de metadados da sessão,
    como data de criação, atualização e estado persistido.

    """
    session_service = request.app.state.session_service
    app_name = app_name or request.app.state.app_name

    session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    state = getattr(session, "state", None) or {}
    raw_messages = state.get("messages", [])

    # -------- Deduplicação --------
    seen = set()
    deduped = []
    for m in raw_messages:
        mid = m.get("id")
        if mid in seen:
            continue
        seen.add(mid)
        deduped.append(m)

    # -------- Tratamento de duplicação do answer --------
    last_assistant_text = None
    if deduped and deduped[-1].get("author") == "assistant":
        last_assistant_text = (deduped[-1].get("text") or "").strip()

    state_for_response = dict(state)
    state_for_response.pop("messages", None)

    for key in (AGENT_OUTPUT_KEY, "answer", "last_answer"):
        if key in state_for_response:
            val = state_for_response.get(key)
            if val is None:
                state_for_response.pop(key, None)
            else:
                try:
                    if last_assistant_text and str(val).strip() == last_assistant_text:
                        state_for_response.pop(key, None)
                except Exception:
                    pass

    messages_out = []
    for m in deduped:
        messages_out.append(SessionMessage(
            id=m.get("id", ""),
            timestamp=m.get("timestamp", 0),
            author=m.get("author", ""),
            role=m.get("role"),
            text=m.get("text")
        ))

    return SessionInfoResponse(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        create_time=getattr(session, "create_time", None),
        update_time=getattr(session, "update_time", None),
        state=state_for_response,
        messages=messages_out,
        events=None
    )


@router.get("/{user_id}/list", response_model=list[SessionListItem])
async def list_user_sessions(user_id: str, request: Request, app_name: Optional[str] = None):
    """
    Lista todas as sessões de um usuário.
    Retorna o id da sessão e a primeira mensagem enviada pelo usuário.
    """
    session_service = request.app.state.session_service
    app_name = app_name or request.app.state.app_name  # garante app_name

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

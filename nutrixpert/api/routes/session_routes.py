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
    session_service = request.app.state.session_service
    app_name = app_name or request.app.state.app_name  

    print(f"[DEBUG] Listando sessões do user_id={user_id}")

    try:
        sessions_resp = await session_service.list_sessions(app_name=app_name, user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar sessões: {e}")

    sessions = getattr(sessions_resp, "sessions", None) or []
    if not sessions:
        raise HTTPException(status_code=404, detail="Nenhuma sessão encontrada para este usuário")

    output = []

    for index, s in enumerate(sessions):
        session_id = getattr(s, "id", None)

        print(f"\n[DEBUG] Buscando state completo da sessão {session_id}")

        full_session = await session_service.get_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )

        if not full_session:
            print(f"[WARN] Sessão {session_id} não encontrada no get_session")
            first_user_msg = None
        else:
            state = getattr(full_session, "state", None) or {}
            raw_messages = state.get("messages", []) or []

            print(f"[DEBUG] RAW MESSAGES: {raw_messages}")

            # --- deduplicação ---
            seen = set()
            deduped = []
            for m in raw_messages:
                mid = m.get("id")
                if mid in seen:
                    continue
                seen.add(mid)
                deduped.append(m)

            # --- busca do first user message ---
            first_user_msg = None
            for m in deduped:
                author = (m.get("author") or m.get("role") or "").lower()
                if author == "user":
                    first_user_msg = (m.get("text") or "").strip()
                    break

        output.append(SessionListItem(
            session_id=session_id,
            first_message=first_user_msg
        ))

    return output


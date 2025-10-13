from fastapi import APIRouter, HTTPException, Request
from typing import Optional
from nutrixpert.core.models import SessionInfoResponse, SessionMessage

router = APIRouter()

AGENT_OUTPUT_KEY = "answer"

@router.get("/sessions/{user_id}/{session_id}", response_model=SessionInfoResponse)
async def get_session_history(user_id: str, session_id: str, request: Request, app_name: Optional[str] = None):
    session_service = request.app.state.session_service
    app_name = app_name or request.app.state.app_name

    session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    state = getattr(session, "state", None) or {}
    raw_messages = state.get("messages", [])

    # --- Deduplicação ---
    seen = set()
    deduped = []
    for m in raw_messages:
        mid = m.get("id")
        if mid in seen:
            continue
        seen.add(mid)
        deduped.append(m)

    # --- Tratamento de duplicação do answer ---
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

    messages_out = [
        SessionMessage(
            id=m.get("id", ""),
            timestamp=m.get("timestamp", 0),
            author=m.get("author", ""),
            role=m.get("role"),
            text=m.get("text")
        )
        for m in deduped
    ]

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

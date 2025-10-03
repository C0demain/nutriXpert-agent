import asyncio
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from google.genai.types import Content, Part

from nutrixpert.core.utils import append_message_to_state
from nutrixpert.agent import AGENT_OUTPUT_KEY

from nutrixpert.rag.rag_service import retrieve_context

router = APIRouter()

# -------- MODELS --------
class AgentRequest(BaseModel):
    user_id: str
    session_id: str
    question: str
    app_name: Optional[str] = None


class SessionMessage(BaseModel):
    id: str
    timestamp: float
    author: str
    role: Optional[str] = None
    text: Optional[str] = None


class SessionInfoResponse(BaseModel):
    app_name: str
    user_id: str
    session_id: str
    create_time: Optional[str] = None
    update_time: Optional[str] = None
    state: Optional[dict] = None
    messages: list[SessionMessage] = []
    events: Optional[list] = None

class SessionListItem(BaseModel):
    session_id: str
    first_message: Optional[str] = None


# -------- ROTAS --------
@router.post("/run-agent")
async def run_agent(req: AgentRequest, request: Request,):

    if not req.user_id or not req.session_id or not req.question:
        raise HTTPException(status_code=400, detail="user_id, session_id and question are required")

    runner = request.app.state.runner
    session_service = request.app.state.session_service
    app_name = req.app_name or request.app.state.app_name

    # 1) garante sessão existente
    session = await session_service.get_session(app_name=app_name, user_id=req.user_id, session_id=req.session_id)
    if session is None:
        session = await session_service.create_session(
            app_name=app_name, user_id=req.user_id, session_id=req.session_id, state={"messages": []}
        )

    # 2) salva mensagem do usuário
    await append_message_to_state(session_service, app_name, req.user_id, req.session_id,
                                  author="user", role="user", text=req.question)

    # 3) injeta contexto do RAG
    context_preview = retrieve_context(req.question)
    question_with_context = f"Contexto relevante dos documentos:\n{context_preview}\n\nPergunta: {req.question}"

    content = Content(role="user", parts=[Part(text=question_with_context)])

    # 4) executa runner
    final_text = ""
    try:
        async for event in runner.run_async(user_id=req.user_id, session_id=req.session_id, new_message=content):
            if getattr(event, "content", None) and getattr(event.content, "parts", None):
                for p in event.content.parts:
                    if getattr(p, "text", None):
                        final_text += p.text
            try:
                if event.is_final_response():
                    break
            except Exception:
                pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ADK runner error: {e}")

    if not final_text:
        raise HTTPException(status_code=502, detail="Agent did not produce a final response")

    # 5) salva resposta do agente
    await append_message_to_state(session_service, app_name, req.user_id, req.session_id,
                                  author="assistant", role="assistant", text=final_text)

    # 6) retorna histórico atualizado
    updated_session = await session_service.get_session(app_name=app_name,
                                                        user_id=req.user_id,
                                                        session_id=req.session_id)
    messages = []
    if updated_session and getattr(updated_session, "state", None):
        messages = updated_session.state.get("messages", [])
        
    # dentro de run_agent, antes de chamar runner.run_async
    context_preview = retrieve_context(req.question)

    return {
        "user_id": req.user_id,
        "session_id": req.session_id,
        "answer": final_text.strip(),
        "history": messages,
        "context_used": context_preview
    }


@router.get("/sessions/{user_id}/{session_id}", response_model=SessionInfoResponse)
async def get_session_history(user_id: str, session_id: str,request: Request, app_name: Optional[str] = None):

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
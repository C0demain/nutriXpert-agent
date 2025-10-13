import asyncio
from fastapi import APIRouter, HTTPException, Request
from google.genai.types import Content, Part
from nutrixpert.utils.utils import append_message_to_state
from nutrixpert.core.tools.retrieve_context import retrieve_context
from nutrixpert.core.models import AgentRequest

router = APIRouter()


@router.post("/run-agent")
async def run_agent(req: AgentRequest, request: Request):
    if not req.user_id or not req.session_id or not req.question:
        raise HTTPException(status_code=400, detail="user_id, session_id and question are required")

    runner = request.app.state.runner
    session_service = request.app.state.session_service
    app_name = req.app_name or request.app.state.app_name

    # 1️⃣ Garante sessão existente
    session = await session_service.get_session(app_name=app_name, user_id=req.user_id, session_id=req.session_id)
    if session is None:
        session = await session_service.create_session(
            app_name=app_name, user_id=req.user_id, session_id=req.session_id, state={"messages": []}
        )

    # 2️⃣ Salva mensagem do usuário
    await append_message_to_state(
        session_service, app_name, req.user_id, req.session_id,
        author="user", role="user", text=req.question
    )

    # 3️⃣ Injeta contexto do RAG
    context_preview = retrieve_context(req.question)
    question_with_context = f"Contexto relevante dos documentos:\n{context_preview}\n\nPergunta: {req.question}"
    content = Content(role="user", parts=[Part(text=question_with_context)])

    # 4️⃣ Executa runner (stream de resposta)
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

    # 5️⃣ Salva resposta do agente
    await append_message_to_state(
        session_service, app_name, req.user_id, req.session_id,
        author="assistant", role="assistant", text=final_text
    )

    # 6️⃣ Retorna histórico atualizado
    updated_session = await session_service.get_session(app_name=app_name, user_id=req.user_id, session_id=req.session_id)
    messages = []
    if updated_session and getattr(updated_session, "state", None):
        messages = updated_session.state.get("messages", [])

    return {
        "user_id": req.user_id,
        "session_id": req.session_id,
        "answer": final_text.strip(),
        "history": messages,
        "context_used": context_preview
    }

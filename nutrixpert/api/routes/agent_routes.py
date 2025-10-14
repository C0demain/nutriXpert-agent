import os
from fastapi import APIRouter, Request, HTTPException
from google.genai.types import Content, Part
from nutrixpert.core.schemas.agent_request import AgentRequest
from nutrixpert.core.tools.retrieve_context import retrieve_context
from nutrixpert.core.tools.feedback_memory import search_related_feedbacks
from nutrixpert.core.utils import append_message_to_state

from dotenv import load_dotenv

load_dotenv()

ADK_APP_NAME = os.getenv("ADK_APP_NAME")

router = APIRouter()

@router.post("/run-agent")
async def run_agent(req: AgentRequest, request: Request):
    """
    Executa o agente de nutrição para responder a uma pergunta do usuário.
    """
    if not req.user_id or not req.session_id or not req.question:
        raise HTTPException(status_code=400, detail="user_id, session_id and question are required")

    runner = request.app.state.runner
    session_service = request.app.state.session_service
    app_name = ADK_APP_NAME

    # Garante sessão
    session = await session_service.get_session(app_name=app_name, user_id=req.user_id, session_id=req.session_id)
    if session is None:
        session = await session_service.create_session(
            app_name=app_name, user_id=req.user_id, session_id=req.session_id, state={"messages": []}
        )

    # Salva mensagem do usuário
    await append_message_to_state(session_service, app_name, req.user_id, req.session_id,
                                  author="user", role="user", text=req.question)

    # Injeta contexto + feedbacks
    context_preview = retrieve_context(req.question)
    feedback_related = search_related_feedbacks(req.question, req.user_id)
    feedback_text = "\n".join([
        f"- Usuário anterior (nota {f['nota']}): {f['comentario']}"
        for f in feedback_related
    ]) if feedback_related else "Nenhum feedback relevante encontrado."

    question_with_context = f"""
    Contexto relevante dos documentos:
    {context_preview}

    Feedbacks do usuário sobre respostas anteriores:
    {feedback_text}

    Pergunta atual:
    {req.question}
    """

    content = Content(role="user", parts=[Part(text=question_with_context)])

    # Executa runner
    final_text = ""
    try:
        async for event in runner.run_async(user_id=req.user_id, session_id=req.session_id, new_message=content):
            if getattr(event, "content", None) and getattr(event.content, "parts", None):
                for p in event.content.parts:
                    if getattr(p, "text", None):
                        final_text += p.text
            if hasattr(event, "is_final_response") and event.is_final_response():
                break
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ADK runner error: {e}")

    if not final_text:
        raise HTTPException(status_code=502, detail="Agent did not produce a final response")

    # Salva resposta do agente
    await append_message_to_state(session_service, app_name, req.user_id, req.session_id,
                                  author="assistant", role="assistant", text=final_text)

    updated_session = await session_service.get_session(app_name=app_name, user_id=req.user_id, session_id=req.session_id)
    messages = updated_session.state.get("messages", []) if updated_session and getattr(updated_session, "state", None) else []

    return {
        "user_id": req.user_id,
        "session_id": req.session_id,
        "answer": final_text.strip(),
        "history": messages,
        "context_used": context_preview
    }

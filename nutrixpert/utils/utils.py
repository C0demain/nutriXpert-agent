import uuid
import time
from google.adk.events import Event, EventActions

async def append_message_to_state(session_service, app_name, user_id, session_id, author, role, text):
    """
    Lê a sessão mais recente, cria um novo messages = old + [entry],
    e usa append_event com EventActions(state_delta={'messages': messages}).
    """
    # pega sessão atual (fresh)
    session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
    if session is None:
        # se por algum motivo não existir, cria com messages vazias
        session = await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id, state={"messages": []})

    old_messages = session.state.get("messages", []) if getattr(session, "state", None) else []
    entry = {
        "id": str(uuid.uuid4()),
        "timestamp": time.time(),
        "author": author,   # ex: "user" ou "assistant" ou "system"
        "role": role,       # opcional: "user" / "assistant"
        "text": text,
    }
    new_messages = old_messages + [entry]

    # cria um evento com state_delta atualizando messages -> new_messages
    actions = EventActions(state_delta={"messages": new_messages})
    event = Event(
        invocation_id=str(uuid.uuid4()),
        author=author,
        actions=actions,
        timestamp=time.time()
    )

    # append_event persiste o novo state e o evento no DB
    await session_service.append_event(session, event)

    # retorna a sessão atualizada (opcional)
    updated = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
    return updated
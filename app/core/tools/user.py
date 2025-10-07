from google.adk.tools import FunctionTool, ToolContext
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def retrieve_user_info(_: Optional[str] = "", tool_context: ToolContext = None) -> dict:
    """
    Mocka a recuperação de informações básicas do usuário.
    Salva os dados no estado da sessão.
    """
    user_id = None
    if tool_context and hasattr(tool_context, "_invocation_context"):
        user_id = getattr(tool_context._invocation_context.session, "user_id", None)
    if not user_id:
        logger.warning("user_id não encontrado no contexto da sessão.")
        return {"status": "error", "message": "user_id não encontrado."}

    data = {
        "nome": "Carlos",
        "idade": 18,
        "peso": 70,
        "altura": 1.75,
        "filmes_favoritos":['Batman','Harry Potter']
    }

    if tool_context is not None:
        tool_context.state["dados_usuario"] = data

    return {"status": "success", "usuario": data}

retrieve_user_info_tool = FunctionTool(
    func=retrieve_user_info,
)

from google.adk.tools import FunctionTool, ToolContext
from typing import Optional

def update_user_info(campo: str, valor: str, tool_context: ToolContext = None) -> dict:
    """
    Atualiza um campo específico do perfil do usuário armazenado no estado.

    Args:
        campo: Nome do campo a ser atualizado.
        valor: Novo valor como string. A função tenta converter automaticamente para int ou float se apropriado.

    Returns:
        dict: Mensagem de status e o estado atualizado.
    """
    if not tool_context:
        return {"status": "error", "message": "ToolContext não disponível."}

    perfil = tool_context.state.get("dados_usuario", {})

    if valor.isdigit():
        parsed_valor = int(valor)
    else:
        try:
            parsed_valor = float(valor)
        except ValueError:
            parsed_valor = valor

    perfil[campo] = parsed_valor
    tool_context.state["dados_usuario"] = perfil

    return {
        "status": "success",
        "message": f"Campo '{campo}' atualizado com sucesso!",
        "dados_usuario": perfil
    }

update_user_info_tool = FunctionTool(func=update_user_info)

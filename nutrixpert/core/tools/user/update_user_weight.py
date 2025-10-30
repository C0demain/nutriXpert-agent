from google.adk.tools import FunctionTool, ToolContext
import requests
import os

TOKEN_LOCAL = os.getenv("TOKEN_LOCAL")

def update_user_weight(user_weight:float, tool_context: ToolContext):
    """
    esta tool serve para atualizar o peso do usuario, se o paciente dizer que seu 
    peso alterou durante a interação é necessário chamar essa função para a atualização
    do peso no sistema e na sua memória
    """

    user_id = None
    if tool_context and hasattr(tool_context, "_invocation_context"):
        user_id = getattr(tool_context._invocation_context.session, "user_id", None)

    if not user_id:
        print("sem userId")
        return {"status": "error", "message": "user_id não encontrado."}
    
    result = update_weight(user_id, user_weight)

    if tool_context is not None and result:
        tool_context.state["userInfo"]["weight"] = user_weight

    return {"status": "sucesso, peso atualizado"}


def update_weight(user_id:str, weight:float):
    url = f"http://localhost:8080/api/interact/agent/physical/{user_id}"
    headers = {
        "LOCAL-TOKEN": TOKEN_LOCAL
    }
    try:
        response = requests.post(url, headers=headers,json={
            "weight": weight
        })
        response.raise_for_status()
        return response.ok
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar usuário: {e}")
        return None


update_user_weight_tool = FunctionTool(
    func = update_user_weight
)
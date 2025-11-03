from google.adk.tools import FunctionTool, ToolContext
import requests
import os

TOKEN_LOCAL = os.getenv("TOKEN_LOCAL")

def update_user_weight(user_weight:float, tool_context: ToolContext):
    """
    esta tool serve para atualizar o peso do usuario, se o paciente dizer que seu 
    peso alterou durante a interação, a função espera receber o peso ja atualizado
    é necessário chamar essa função para a atualização
    do peso no sistema e na sua memória
    """

    user_id = None
    if tool_context and hasattr(tool_context, "_invocation_context"):
        user_id = getattr(tool_context._invocation_context.session, "user_id", None)

    if not user_id:
        print("sem userId")
        return {"status": "error", "message": "user_id não encontrado."}

    updated_user = patch_user_weight(user_id, user_weight)

    if updated_user and tool_context is not None:
        # Atualiza o state local com os dados mais recentes do usuário
        tool_context.state["userInfo"] = updated_user

    return {
        "status": "success" if updated_user else "error",
        "usuario": updated_user
    }


def patch_user_weight(user_id: str, weight: float) -> dict | None:
    """
    Chama o backend para atualizar o peso e retorna o JSON atualizado do usuário.
    """
    url = f"http://localhost:8080/api/interact/agent/physical/{user_id}"
    headers = {
        "LOCAL-TOKEN": TOKEN_LOCAL
    }
    try:
        response = requests.patch(url, headers=headers, json={"weight": weight})
        print(f"[DEBUG] PATCH {url} -> {response.status_code}: {response.text}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao atualizar peso: {e}")
        return None

update_user_weight_tool = FunctionTool(
    func = update_user_weight
)
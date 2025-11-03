from google.adk.tools import FunctionTool, ToolContext
import requests
import os


TOKEN_LOCAL = os.getenv("TOKEN_LOCAL")

def retrieve_user_info(tool_context: ToolContext) -> dict:
    """
    recupera as informações do usuario atraves do id que existe no state
    consulta a api do backend com o banco de dados, recupera as informações do usuario
    e adiciona ao state da session para utilização futura
    """

    user_id = None
    if tool_context and hasattr(tool_context, "_invocation_context"):
        user_id = getattr(tool_context._invocation_context.session, "user_id", None)
    
    if not user_id:
        print("sem userId")
        return {"status": "error", "message": "user_id não encontrado."}
    
    user = get_user(user_id)

    if tool_context is not None:
        tool_context.state["userInfo"] = user



    return {"status": "success", "usuario": user}



def get_user(user_id: str) -> dict:
    url = f"http://localhost:8080/api/interact/agent/getUserInfo/{user_id}"
    headers = {
        "LOCAL-TOKEN": TOKEN_LOCAL
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar usuário: {e}")
        return None


retrieve_user_info_tool = FunctionTool(
    func=retrieve_user_info,
)
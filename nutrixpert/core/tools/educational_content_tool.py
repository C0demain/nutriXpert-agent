from google.adk.tools import FunctionTool

def educational_response(topic: str):
    """
    Retorna explicações conceituais sobre nutrição (índice glicêmico, vitaminas, etc.).
    """
    return f"Explicação detalhada sobre {topic}: ... (conteúdo proveniente da base educacional)"

educational_content_tool = FunctionTool(
    func=educational_response
)

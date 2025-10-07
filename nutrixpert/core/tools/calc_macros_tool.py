from google.adk.tools import FunctionTool

def calc_macros(calorias: int, objetivo: str = "manutencao"):
    """
    Calcula a distribuição de macros (carboidratos, proteínas, gorduras)
    conforme o objetivo: 'emagrecimento', 'manutencao' ou 'ganho'.
    """
    objetivos = {
        "emagrecimento": (0.45, 0.35, 0.20),
        "manutencao": (0.50, 0.30, 0.20),
        "ganho": (0.55, 0.25, 0.20),
    }

    carb, prot, gord = objetivos.get(objetivo.lower(), (0.5, 0.3, 0.2))
    return {
        "Carboidratos (g)": round((calorias * carb) / 4, 1),
        "Proteínas (g)": round((calorias * prot) / 4, 1),
        "Gorduras (g)": round((calorias * gord) / 9, 1),
    }

calc_macros_tool = FunctionTool(
    func=calc_macros,
)

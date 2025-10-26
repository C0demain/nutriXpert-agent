from google.adk.tools import FunctionTool

def meal_plan(calorias: int, refeicoes: int = 5):
    """
    Gera um plano alimentar diário com base nas calorias desejadas e número de refeições.
    """
    por_refeicao = calorias / refeicoes
    
    return {
        "meta_diaria_kcal": calorias,
        "refeicoes": [
            {"refeicao": f"Refeição {i+1}", "meta_kcal": round(por_refeicao, 2)}
            for i in range(refeicoes)
        ],
    }

meal_plan_tool = FunctionTool(
    func=meal_plan,
)

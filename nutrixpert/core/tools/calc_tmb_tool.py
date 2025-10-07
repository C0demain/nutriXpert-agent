from google.adk.tools import FunctionTool

def calc_tmb(sexo: str, idade: int, peso: float, altura: float, nivel_atividade: str = "moderado"):
    """
    Calcula a Taxa Metabólica Basal (TMB) e gasto calórico diário estimado.
    Fórmula de Mifflin-St Jeor.
    """
    if sexo.lower() == "masculino":
        tmb = 10 * peso + 6.25 * altura - 5 * idade + 5
    else:
        tmb = 10 * peso + 6.25 * altura - 5 * idade - 161

    fatores = {
        "sedentario": 1.2,
        "leve": 1.375,
        "moderado": 1.55,
        "intenso": 1.725,
        "muito_intenso": 1.9,
    }

    gasto_total = tmb * fatores.get(nivel_atividade.lower(), 1.55)
    return {
        "TMB (kcal)": round(tmb, 2),
        "Gasto Diário Estimado (kcal)": round(gasto_total, 2),
    }

calc_tmb_tool = FunctionTool(
    func=calc_tmb,
)

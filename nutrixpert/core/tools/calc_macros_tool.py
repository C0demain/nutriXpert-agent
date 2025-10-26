from google.adk.tools import FunctionTool

def calc_macros(peso: float, calorias: int, objetivo: str = "manutencao"):
    """
    Calcula a distribuição de macros (carboidratos, proteínas, gorduras)
    com base no peso corporal e no objetivo:
    'emagrecimento', 'manutencao' ou 'ganho'.

    Retorna valores em gramas e percentuais estimados.
    """
    # Definições médias de ingestão (g/kg)
    if objetivo.lower() == "emagrecimento":
        proteina_gkg = 2.0
        gordura_gkg = 0.8
    elif objetivo.lower() == "ganho":
        proteina_gkg = 1.6
        gordura_gkg = 1.0
    else:  # manutenção
        proteina_gkg = 1.8
        gordura_gkg = 0.9

    # Cálculo base
    proteinas = peso * proteina_gkg
    gorduras = peso * gordura_gkg

    # Calorias parciais
    kcal_prot = proteinas * 4
    kcal_gord = gorduras * 9

    # Calorias restantes vão para carboidratos
    kcal_carb = calorias - (kcal_prot + kcal_gord)
    carboidratos = kcal_carb / 4

    # Percentuais finais
    total_kcal = kcal_prot + kcal_gord + kcal_carb
    perc_prot = round((kcal_prot / total_kcal) * 100, 1)
    perc_gord = round((kcal_gord / total_kcal) * 100, 1)
    perc_carb = round((kcal_carb / total_kcal) * 100, 1)

    return {
        "Carboidratos (g)": round(carboidratos, 1),
        "Proteínas (g)": round(proteinas, 1),
        "Gorduras (g)": round(gorduras, 1),
        "Distribuição (%)": {
            "Carboidratos": perc_carb,
            "Proteínas": perc_prot,
            "Gorduras": perc_gord,
        },
        "Total (kcal)": round(total_kcal),
    }

calc_macros_tool = FunctionTool(
    func=calc_macros
)

from google.adk.tools import FunctionTool, ToolContext
import requests
import os
from typing import Optional
from pydantic import ValidationError

from .anamnese_schemas import AnamneseUpdate

TOKEN_LOCAL = os.getenv("TOKEN_LOCAL")

def update_user_anamnese(
    tool_context: ToolContext,

    goalType: Optional[str] = None,
    goalTypeOther: Optional[str] = None,
    healthConditionType: Optional[str] = None,
    healthConditionOther: Optional[str] = None,
    allergyIntoleranceType: Optional[str] = None,
    allergyIntoleranceOther: Optional[str] = None,
    surgeryType: Optional[str] = None,
    surgeryTypeOther: Optional[str] = None,
    physicalActivityType: Optional[str] = None,
    physicalActivityOther: Optional[str] = None,
    physicalActivityFrequency: Optional[str] = None,
    physicalActivityDuration: Optional[str] = None,
    sleepQuality: Optional[str] = None,
    nightAwakeningFrequency: Optional[str] = None,
    evacuationFrequencyType: Optional[str] = None,
    stressLevel: Optional[str] = None,
    alcoholConsumption: Optional[str] = None,
    tabagism: Optional[bool] = None,
    hydration: Optional[str] = None,
    continuousMedication: Optional[bool] = None

) -> dict:
    """
    Atualiza um ou mais campos da anamnese do usuário.
    Esta ferramenta recebe apenas os campos que precisam ser alterados e
    envia uma requisição PATCH para o backend.
    """

    user_id = None
    if tool_context and hasattr(tool_context, "_invocation_context"):
        user_id = getattr(tool_context._invocation_context.session, "user_id", None)
    
    if not user_id:
        print("sem userId")
        return {"status": "error", "message": "user_id não encontrado."}
    
    try:
        patch_data = AnamneseUpdate(
            goalType=goalType,
            goalTypeOther=goalTypeOther,
            healthConditionType=healthConditionType,
            healthConditionOther=healthConditionOther,
            allergyIntoleranceType=allergyIntoleranceType,
            allergyIntoleranceOther=allergyIntoleranceOther,
            surgeryType=surgeryType,
            surgeryTypeOther=surgeryTypeOther,
            physicalActivityType=physicalActivityType,
            physicalActivityOther=physicalActivityOther,
            physicalActivityFrequency=physicalActivityFrequency,
            physicalActivityDuration=physicalActivityDuration,
            sleepQuality=sleepQuality,
            nightAwakeningFrequency=nightAwakeningFrequency,
            evacuationFrequencyType=evacuationFrequencyType,
            stressLevel=stressLevel,
            alcoholConsumption=alcoholConsumption,
            tabagism=tabagism,
            hydration=hydration,
            continuousMedication=continuousMedication
        )
    except ValidationError as e:
        print(f"Erro de validação do Pydantic ao criar AnamneseUpdate: {e}")
        return {"status": "error", "message": f"Erro de validação interna: {e}"}

    payload_dict = patch_data.model_dump(exclude_unset=True)


    if not payload_dict:
        print("O agente chamou update_user_anamnese sem fornecer nenhum campo.")
        return {"status": "error", "message": "Nenhum campo de atualização foi fornecido."}

    updated_user = patch_anamnese(user_id=user_id, payload=payload_dict)

    if updated_user and tool_context is not None:
        tool_context.state["userInfo"] = updated_user

    return {
        "status": "success" if updated_user else "error",
        "message": "Anamnese atualizada com sucesso" if updated_user else "Falha ao atualizar anamnese.",
        "usuario": updated_user
    }


def patch_anamnese(user_id: str, payload: dict) -> dict | None:
    """
    Chama o backend (PATCH) para atualizar a anamnese com um payload parcial.
    """
    url = f"http://localhost:8080/api/interact/agent/{user_id}/anamnese"
    
    if not TOKEN_LOCAL:
        print("Erro: TOKEN_LOCAL não está definido nas variáveis de ambiente.")
        return None

    headers = {
        "LOCAL-TOKEN": TOKEN_LOCAL
    }
    
    try:
        print(f"[DEBUG] PATCH {url} -> Payload: {payload}")
        response = requests.patch(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP ao atualizar anamnese: {http_err} - Resposta: {response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Erro de Request ao atualizar anamnese: {e}")
        return None


update_user_anamnese_tool = FunctionTool(
    func=update_user_anamnese, 
)
from google.adk.tools import FunctionTool, ToolContext
import requests
import os
from .anamnese_schemas import AnamneseCreate
from pydantic import ValidationError
from typing import Optional


TOKEN_LOCAL = os.getenv("TOKEN_LOCAL")

def create_user_anamnese(tool_context: ToolContext,
    
    goalType: Optional[str] = None,
    goalTypeOther: str = "",
    healthConditionType: Optional[str] = None,
    healthConditionOther: str = "",
    allergyIntoleranceType: Optional[str] = None,
    allergyIntoleranceOther: str = "",
    surgeryType: Optional[str] = None,
    surgeryTypeOther: str = "",
    physicalActivityType: Optional[str] = None,
    physicalActivityOther: str = "",
    physicalActivityFrequency: Optional[str] = None,
    physicalActivityDuration: Optional[str] = None,
    sleepQuality: Optional[str] = None,
    nightAwakeningFrequency: Optional[str] = None,
    evacuationFrequencyType: Optional[str] = None,
    stressLevel: Optional[str] = None,
    alcoholConsumption: Optional[str] = None,
    tabagism: Optional[bool] = None,
    hydration: Optional[str] = None,
    continuousMedication: Optional[bool] = None) -> dict:
    """

    cria uma anamnese para o usuario após a coleta de informações
    via chat, deve ser seguido o modelo de informação especificado pelo schema AnamneseCreate
    essa ferramenta ira criar a anamnese para o usuario e atualizar o state com as 
    novas informações 
    
    """

    user_id = None
    if tool_context and hasattr(tool_context, "_invocation_context"):
        user_id = getattr(tool_context._invocation_context.session, "user_id", None)
    
    if not user_id:
        print("sem userId")
        return {"status": "error", "message": "user_id não encontrado."}
    
    try:
        userAnamnese = AnamneseCreate(
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
        print(f"Erro de validação do Pydantic ao criar AnamneseCreate: {e}")
        return {"status": "error", "message": f"Erro de validação interna: {e}"}
    
    userInfo = create_anamnese(user_id=user_id, anamnese=userAnamnese)

    if userInfo is None:
        print(f"Falha ao criar anamnese para o usuário {user_id}")
        return {"status": "error", "message": "Não foi possível criar a anamnese no backend."}

    if tool_context is not None:
        tool_context.state["userInfo"] = userInfo



    return {"status": "success", "usuario": userInfo}



def create_anamnese(user_id: str, anamnese: AnamneseCreate) -> dict:
    url = f"http://localhost:8080/api/interact/agent/{user_id}/anamnese"
    headers = {
        "LOCAL-TOKEN": TOKEN_LOCAL
    }
    payload = anamnese.model_dump()
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar usuário: {e}")
        return None


create_user_anamnese_tool = FunctionTool(
    func=create_user_anamnese
)
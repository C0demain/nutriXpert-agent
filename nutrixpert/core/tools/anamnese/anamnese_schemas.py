import pydantic
from enum import Enum
from typing import Optional, Union


class GoalType(str, Enum):
    EMAGRECIMENTO = "Emagrecimento"
    GANHO_MASSA = "Ganho de massa muscular"
    CONTROLE_DIABETES = "Controle de diabetes"
    REEDUCACAO = "Reeducação alimentar"
    PERFORMANCE = "Performance física e mental"
    GANHO_PESO = "Ganho de peso"
    PERDA_GORDURA = "Perda de gordura"
    MANUTENCAO = "Manutenção do peso"

class HealthConditionType(str, Enum):
    DIABETES_1 = "Diabetes tipo 1"
    DIABETES_2 = "Diabetes tipo 2"
    HIPERTENSAO = "Hipertensão arterial"
    DISLIPIDEMIA = "Dislipidemia (colesterol, triglicerídeos)"
    RENAL = "Doença renal"
    HEPATICA = "Doença hepática"
    GASTRITE = "Gastrite / refluxo"
    INTESTINO = "Intestino preso / diarreia"
    OSTEOPOROSE = "Osteoporose"
    CARDIOVASCULAR = "Doença cardiovascular (infarto, insuficiência cardíaca)"
    CANCER = "Câncer"
    DEPRESSAO_ANSIEDADE = "Depressão / Ansiedade"
    AUTOIMUNE = "Doenças autoimunes"
    OUTRO = "Outro"

class AllergyIntoleranceType(str, Enum):
    NAO = "Não"
    LACTOSE = "Intolerância à lactose"
    GLUTEN = "Sensibilidade ao glúten / doença celíaca"
    ALIMENTAR = "Alergia alimentar"
    MEDICAMENTOSA = "Alergia medicamentosa"
    OUTRO = "Outro"

class SurgeryType(str, Enum):
    NAO = "não"
    BARIATRICA = "Bariátrica"
    VESICULA = "Vesícula"
    HERNIA_HIATO = "Hérnia de hiato (cirurgia do refluxo)"
    ORTOPEDICA = "Ortopédica"
    GINECOLOGICA = "Cesárea / Ginecológica"
    OUTRO = "Outro"

class PhysicalActivityType(str, Enum):
    SEDENTARIO = "Sedentário(a)"
    CAMINHADA = "Caminhada"
    MUSCULACAO = "Musculação"
    CORRIDA = "Corrida"
    CROSSFIT = "Crossfit"
    NATACAO = "Natação"
    OUTRO = "Outro"

class PhysicalActivityFrequency(str, Enum):
    FREQ_1_2 = "1–2x por semana"
    FREQ_3_4 = "3–4x por semana"
    FREQ_5_MAIS = "5 ou mais vezes por semana"

class PhysicalActivityDuration(str, Enum):
    DUR_30 = "30 min"
    DUR_60 = "60 min"
    DUR_90 = "90 min"

class SleepQuality(str, Enum):
    BOA = "boa"
    REGULAR = "regular"
    RUIM = "ruim"

class NightAwakeningFrequency(str, Enum):
    NAO = "nao"
    UMA_VEZ = "pelo menos uma vez"
    MAIS_DE_UMA = "mais de uma vez"

class EvacuationFrequencyType(str, Enum):
    TODO_DIA = "Todo dia"
    FREQ_5 = "5x por semana"
    FREQ_3 = "3x por semana"
    FREQ_1 = "1x por semana"

class StressLevel(str, Enum):
    BAIXO = "baixo"
    MODERADO = "moderado"
    ALTO = "alto"

class AlcoholConsumption(str, Enum):
    NAO_CONSOME = "não consome"
    SOCIALMENTE = "Socialmente 1-2 x por semana"
    FREQUENTE = "Frequente 3-4 x por semana"
    DIARIO = "Uso diário"

class Hydration(str, Enum):
    MENOS_1L = "Menos de 1L"
    ENTRE_1L_2L = "Entre 1L e 2L"
    MAIS_2L = "Mais de 2L"


class AnamneseCreate(pydantic.BaseModel):
    """
    Schema de entrada para a tool 'create_user_anamnese'.
    Exige todos os campos, permitindo 'null' para enums/bools.
    """
    goalType: Optional[GoalType] = None 
    goalTypeOther: str = pydantic.Field(default="")
    
    healthConditionType: Optional[HealthConditionType] = None
    healthConditionOther: str = pydantic.Field(default="")
    
    allergyIntoleranceType: Optional[AllergyIntoleranceType] = None
    allergyIntoleranceOther: str = pydantic.Field(default="")
    
    surgeryType: Optional[SurgeryType] = None
    surgeryTypeOther: str = pydantic.Field(default="")
    
    physicalActivityType: Optional[PhysicalActivityType] = None
    physicalActivityOther: str = pydantic.Field(default="")
    physicalActivityFrequency: Optional[PhysicalActivityFrequency] = None
    physicalActivityDuration: Optional[PhysicalActivityDuration] = None
    
    sleepQuality: Optional[SleepQuality] = None
    nightAwakeningFrequency: Optional[NightAwakeningFrequency] = None
    evacuationFrequencyType: Optional[EvacuationFrequencyType] = None
    stressLevel: Optional[StressLevel] = None
    
    alcoholConsumption: Optional[AlcoholConsumption] = None
    
    tabagism: Optional[bool] = None
    
    hydration: Optional[Hydration] = None
    
    continuousMedication: Optional[bool] = None

    class Config:
        use_enum_values = True



class AnamneseUpdate(pydantic.BaseModel):
    """
    Schema de entrada para a tool 'update_user_anamnese'.
    Todos os campos são opcionais para permitir atualizações parciais (PATCH).
    """
    goalType: Optional[GoalType] = None
    goalTypeOther: Optional[str] = None
    
    healthConditionType: Optional[HealthConditionType] = None
    healthConditionOther: Optional[str] = None
    
    allergyIntoleranceType: Optional[AllergyIntoleranceType] = None
    allergyIntoleranceOther: Optional[str] = None
    
    surgeryType: Optional[SurgeryType] = None
    surgeryTypeOther: Optional[str] = None
    
    physicalActivityType: Optional[PhysicalActivityType] = None
    physicalActivityOther: Optional[str] = None
    physicalActivityFrequency: Optional[PhysicalActivityFrequency] = None
    physicalActivityDuration: Optional[PhysicalActivityDuration] = None
    
    sleepQuality: Optional[SleepQuality] = None
    nightAwakeningFrequency: Optional[NightAwakeningFrequency] = None
    evacuationFrequencyType: Optional[EvacuationFrequencyType] = None
    stressLevel: Optional[StressLevel] = None
    
    alcoholConsumption: Optional[AlcoholConsumption] = None
    
    tabagism: Optional[bool] = None
    
    hydration: Optional[Hydration] = None
    
    continuousMedication: Optional[bool] = None

    class Config:
        use_enum_values = True
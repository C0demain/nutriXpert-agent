from google.adk.agents import Agent, LlmAgent
from google.genai import types
from nutrixpert.core.tools import (
    calc_macros_tool,
    retrieve_context_tool,
    query_alimentos_tool,
    calc_tmb_tool,
    meal_plan_tool,
    educational_content_tool,
    retrieve_user_info_tool,
    update_user_weight_tool,
    create_user_anamnese_tool,
    update_user_anamnese_tool
)
from nutrixpert.core.prompt import (
    ROOT_AGENT_INSTR, 
    AGENT_NUTRICAO_INSTR, 
    AGENT_METABOLICO_INSTR, 
    AGENT_PLANEJAMENTO_INSTR, 
    AGENT_EDUCATIVO_INSTR,
    AGENT_ANAMNESE_INSTR
)
from nutrixpert.core.utils.constants import ADK_APP_NAME, ADK_MODEL, AGENT_OUTPUT_KEY


def build_nutricional_agent() -> Agent:
    """Agente especialista em composição e substituições alimentares"""
    return LlmAgent(
        name="Agente_Nutricional",
        model=ADK_MODEL,
        description="Especialista em composição e substituições alimentares",
        instruction=AGENT_NUTRICAO_INSTR,
        output_key=AGENT_OUTPUT_KEY,
        tools=[
            query_alimentos_tool, 
            retrieve_context_tool,
            retrieve_user_info_tool
        ],
        include_contents="default",
        generate_content_config=types.GenerateContentConfig(
            temperature=0.3,  # mais exato, menos criativo
            safety_settings=[
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                )
            ],
        ),
    )

def build_anamnese_agent() -> Agent:
    """Agente responsável por criar e atualizar a anamnese do paciente"""
    return LlmAgent(
        name="Agente_Anamnese",
        model=ADK_MODEL,
        description="agente especializado em criar e atualizar anamneses",
        instruction=AGENT_ANAMNESE_INSTR,
        output_key=AGENT_OUTPUT_KEY,
        tools=[create_user_anamnese_tool, update_user_anamnese_tool],
        include_contents="default",
        generate_content_config=types.GenerateContentConfig(
            temperature=0.3,
            safety_settings=[
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                )
            ],
        ),
    )


def build_metabolico_agent() -> Agent:
    """Agente responsável por cálculos de metabolismo e TMB"""
    return LlmAgent(
        name="Agente_Metabolico",
        model=ADK_MODEL,
        description="Responsável por cálculos de metabolismo e TMB",
        instruction=AGENT_METABOLICO_INSTR,
        output_key=AGENT_OUTPUT_KEY,
        tools=[
            calc_tmb_tool, 
            calc_macros_tool,
            retrieve_user_info_tool
        ],
        include_contents="default",
        generate_content_config=types.GenerateContentConfig(
            temperature=0.2,  # respostas mais determinísticas
            safety_settings=[
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                )
            ],
        ),
    )


def build_planejamento_agent() -> Agent:
    """Agente para planejamento de cardápios"""
    return LlmAgent(
        name="Agente_Planejamento",
        model=ADK_MODEL,
        description="Especialista em planejamento de cardápios",
        instruction=AGENT_PLANEJAMENTO_INSTR,
        output_key=AGENT_OUTPUT_KEY,
        tools=[
            meal_plan_tool, 
            update_user_weight_tool,
            retrieve_user_info_tool
        ],
        include_contents="default",
        generate_content_config=types.GenerateContentConfig(
            temperature=0.7,  # mais criativo para sugerir combinações
            safety_settings=[
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                )
            ],
        ),
    )


def build_educativo_agent() -> Agent:
    """Agente que responde dúvidas teóricas sobre nutrição"""
    return LlmAgent(
        name="Agente_Educativo",
        model=ADK_MODEL,
        description="Responde dúvidas teóricas sobre nutrição",
        instruction=AGENT_EDUCATIVO_INSTR,
        output_key=AGENT_OUTPUT_KEY,
        tools=[
            educational_content_tool,
            retrieve_user_info_tool
        ],
        include_contents="default",
        generate_content_config=types.GenerateContentConfig(
            temperature=0.6,  # tom mais natural e explicativo
            safety_settings=[
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                )
            ],
        ),
    )


def build_root_agent() -> Agent:
    """Coordenador que entende o contexto e decide qual subagente usar"""
    nutricional = build_nutricional_agent()
    metabolico = build_metabolico_agent()
    planejamento = build_planejamento_agent()
    educativo = build_educativo_agent()
    anamnese = build_anamnese_agent()

    return LlmAgent(
        name=ADK_APP_NAME,
        model=ADK_MODEL,
        instruction=ROOT_AGENT_INSTR,
        description="Gerencia o fluxo entre subagentes de nutrição",
        tools=[retrieve_user_info_tool],
        sub_agents=[nutricional, metabolico, planejamento, educativo, anamnese],
        include_contents="default",
        generate_content_config=types.GenerateContentConfig(
            temperature=0.5,  # equilíbrio entre lógica e flexibilidade
            safety_settings=[
                types.SafetySetting(
                    category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                )
            ],
        ),
    )


# instancia final
root_agent = build_root_agent()

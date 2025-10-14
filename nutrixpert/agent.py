import os
from dotenv import load_dotenv
from google.adk.agents import Agent, LlmAgent
from nutrixpert.core.tools import (
    calc_macros_tool,
    retrieve_context_tool,
    query_alimentos_tool,
    calc_tmb_tool,
    meal_plan_tool,
    educational_content_tool
)
from nutrixpert.core.prompt import (
    ROOT_AGENT_INSTR, 
    AGENT_NUTRICAO_INSTR, 
    AGENT_METABOLICO_INSTR, 
    AGENT_PLANEJAMENTO_INSTR, 
    AGENT_EDUCATIVO_INSTR
)

load_dotenv()

ADK_APP_NAME = os.getenv("ADK_APP_NAME")
AGENT_OUTPUT_KEY = "answer"
ADK_MODEL = os.getenv("ADK_MODEL")

def build_nutricional_agent() -> Agent:
    """Agente especialista em composição e substituições alimentares"""

    return LlmAgent(
        name="Agente_Nutricional",
        model=ADK_MODEL,
        instruction=AGENT_NUTRICAO_INSTR,
        output_key=AGENT_OUTPUT_KEY,
        tools=[
            query_alimentos_tool, 
            retrieve_context_tool
        ],
        include_contents="default",
    )                               


def build_metabolico_agent() -> Agent:
    
    """Agente responsável por cálculos de metabolismo e TMB"""
    return LlmAgent(
        name="Agente_Metabolico",
        model=ADK_MODEL,
        instruction=AGENT_METABOLICO_INSTR,
        output_key=AGENT_OUTPUT_KEY,
        tools=[
            calc_tmb_tool, 
            calc_macros_tool
        ],
        include_contents="default",
    )


def build_planejamento_agent() -> Agent:
    """Agente para planejamento de cardápios"""
    return LlmAgent(
        name="Agente_Planejamento",
        model=ADK_MODEL,
        instruction=AGENT_PLANEJAMENTO_INSTR,
        output_key=AGENT_OUTPUT_KEY,
        tools=[
            meal_plan_tool
        ],
        include_contents="default",
    )


def build_educativo_agent() -> Agent:
    """Agente que responde dúvidas teóricas sobre nutrição"""
    return LlmAgent(
        name="Agente_Educativo",
        model=ADK_MODEL,
        instruction=AGENT_EDUCATIVO_INSTR,
        output_key=AGENT_OUTPUT_KEY,
        tools=[
            educational_content_tool
        ],
        include_contents="default",
    )


def build_root_agent() -> Agent:
    """Coordenador que entende o contexto e decide qual subagente usar"""
    nutricional = build_nutricional_agent()
    metabolico = build_metabolico_agent()
    planejamento = build_planejamento_agent()
    educativo = build_educativo_agent()

    root_agent = LlmAgent(
        name=ADK_APP_NAME,
        model=ADK_MODEL,
        instruction=ROOT_AGENT_INSTR,
        description="Gerencia o fluxo entre subagentes de nutrição",
        sub_agents=[
            nutricional, 
            metabolico, 
            planejamento, 
            educativo
        ],
        include_contents="default",
    )
    return root_agent


# instancia final
root_agent = build_root_agent()

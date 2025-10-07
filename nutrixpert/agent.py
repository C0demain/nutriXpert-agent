import os
from dotenv import load_dotenv
from google.adk.agents import Agent, LlmAgent
from nutrixpert.core.tools.retrieve_context import retrieve_context_tool
from nutrixpert.core.tools.retrieve_taco_data import query_alimentos_tool
from nutrixpert.core.tools.calc_tmb_tool import calc_tmb_tool
from nutrixpert.core.tools.meal_plan_tool import meal_plan_tool
from nutrixpert.core.tools.educational_content_tool import educational_content_tool
from google.adk.models.lite_llm import LiteLlm

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
    ollama_medgemma = LiteLlm(
        model=ADK_MODEL
    )

    return LlmAgent(
        name="Agente_Nutricional",
        model=ollama_medgemma,
        instruction=AGENT_NUTRICAO_INSTR,
        output_key=AGENT_OUTPUT_KEY,
        tools=[query_alimentos_tool, retrieve_context_tool],
        include_contents="default",
    )                               


def build_metabolico_agent() -> Agent:
    
    """Agente responsável por cálculos de metabolismo e TMB"""
    return LlmAgent(
        name="Agente_Metabolico",
        model="gemini-2.0-flash", # modelo especializado médico
        instruction=AGENT_METABOLICO_INSTR,
        output_key=AGENT_OUTPUT_KEY,
        tools=[calc_tmb_tool],
        include_contents="default",
    )


def build_planejamento_agent() -> Agent:
    """Agente para planejamento de cardápios"""
    return LlmAgent(
        name="Agente_Planejamento",
        model="gemini-2.0-flash",
        instruction=AGENT_PLANEJAMENTO_INSTR,
        output_key=AGENT_OUTPUT_KEY,
        tools=[meal_plan_tool],
        include_contents="default",
    )


def build_educativo_agent() -> Agent:
    """Agente que responde dúvidas teóricas sobre nutrição"""
    return LlmAgent(
        name="Agente_Educativo",
        model="gemini-2.0-flash",
        instruction=AGENT_EDUCATIVO_INSTR,
        output_key=AGENT_OUTPUT_KEY,
        tools=[educational_content_tool],
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
        model="gemini-2.0-flash",
        instruction=ROOT_AGENT_INSTR,
        sub_agents=[nutricional, metabolico, planejamento, educativo],
        include_contents="default",
    )
    return root_agent


# instancia final
root_agent = build_root_agent()

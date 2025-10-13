import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from nutrixpert.core.agents.root_agent_prompt import ROOT_AGENT_INSTR
from nutrixpert.core.subagents.nutricional_agent.nutricional_agent import build_nutricional_agent
from nutrixpert.core.subagents.metabolico_agent.metabolico_agent import build_metabolico_agent
from nutrixpert.core.subagents.planejamento_agent.planejamento_agent import build_planejamento_agent

load_dotenv()

ADK_APP_NAME = os.getenv("ADK_APP_NAME")


def build_root_agent() -> LlmAgent:
    """Coordenador que entende o contexto e decide qual subagente usar"""
    nutricional = build_nutricional_agent()
    metabolico = build_metabolico_agent()
    planejamento = build_planejamento_agent()

    root_agent = LlmAgent(
        name=ADK_APP_NAME,
        model="gemini-2.0-flash",
        instruction=ROOT_AGENT_INSTR,
        description="Gerencia o fluxo entre subagentes de nutrição",
        sub_agents=[
            nutricional, 
            metabolico, 
            planejamento
        ],
        include_contents="default",
    )
    return root_agent


# Instância global opcional
root_agent = build_root_agent()

import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from nutrixpert.core.tools import query_alimentos_tool, retrieve_context_tool
from nutrixpert.core.subagents.nutricional_agent.nutricional_prompt import AGENT_NUTRICAO_INSTR

load_dotenv()

ADK_MODEL = os.getenv("ADK_MODEL")
AGENT_OUTPUT_KEY = "answer"


def build_nutricional_agent() -> LlmAgent:
    """Agente especialista em composição e substituições alimentares"""
    ollama_medgemma = LiteLlm(model=ADK_MODEL)

    return LlmAgent(
        name="Agente_Nutricional",
        model="gemini-2.0-flash",
        instruction=AGENT_NUTRICAO_INSTR,
        output_key=AGENT_OUTPUT_KEY,
        tools=[
            query_alimentos_tool,
            retrieve_context_tool,
        ],
        include_contents="none",
    )

nutricional_agent = build_nutricional_agent()
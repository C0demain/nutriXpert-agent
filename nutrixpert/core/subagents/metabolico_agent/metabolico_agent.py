from google.adk.agents import LlmAgent
from nutrixpert.core.tools import calc_tmb_tool, calc_macros_tool
from nutrixpert.core.subagents.metabolico_agent.metabolico_prompt import AGENT_METABOLICO_INSTR

AGENT_OUTPUT_KEY = "answer"

def build_metabolico_agent() -> LlmAgent:
    """Agente responsável por cálculos de metabolismo e TMB"""
    return LlmAgent(
        name="Agente_Metabolico",
        model="gemini-2.0-flash",  # modelo especializado médico
        instruction=AGENT_METABOLICO_INSTR,
        output_key=AGENT_OUTPUT_KEY,
        tools=[
            calc_tmb_tool,
            calc_macros_tool,
        ],
    )

metabolico_agent = build_metabolico_agent()
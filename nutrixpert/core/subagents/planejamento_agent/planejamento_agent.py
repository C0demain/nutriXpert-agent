from google.adk.agents import LlmAgent
from nutrixpert.core.tools import meal_plan_tool
from nutrixpert.core.subagents.planejamento_agent.planejamento_prompt import AGENT_PLANEJAMENTO_INSTR

AGENT_OUTPUT_KEY = "answer"

def build_planejamento_agent() -> LlmAgent:
    """Agente para planejamento de cardápios"""
    return LlmAgent(
        name="Agente_Planejamento",
        model="gemini-2.0-flash",
        instruction=AGENT_PLANEJAMENTO_INSTR,
        output_key=AGENT_OUTPUT_KEY,
        tools=[
            meal_plan_tool
        ],
    )

planejamento_agent = build_planejamento_agent()
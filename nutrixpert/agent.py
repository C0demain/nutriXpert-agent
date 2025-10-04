import os
import asyncio
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.agents import LlmAgent

from google.adk.models.lite_llm import LiteLlm

from nutrixpert.core.prompt import ROOT_AGENT_INSTR
from nutrixpert.core.tools.retrieve_context import retrieve_context_tool, get_taco_vectorstore_tool

# carregar variáveis de ambiente
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
ADK_APP_NAME = os.getenv("ADK_APP_NAME")
ADK_MODEL = os.getenv("ADK_MODEL")
ADK_SERIALIZE_RUNNER = os.getenv("ADK_SERIALIZE_RUNNER", "false").lower() in ("1", "true", "yes")
AGENT_OUTPUT_KEY = "answer"


def build_agent() -> Agent:
    
    root_agent = LlmAgent(
        name=ADK_APP_NAME,
        model="gemini-2.0-flash",
        instruction=ROOT_AGENT_INSTR,
        output_key=AGENT_OUTPUT_KEY,
        tools=[
            retrieve_context_tool,
            get_taco_vectorstore_tool
        ],  
        include_contents="default"
    )
    return root_agent

root_agent = build_agent()

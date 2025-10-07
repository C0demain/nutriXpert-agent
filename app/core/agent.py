import os
import asyncio
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.adk.models.lite_llm import LiteLlm
from .tools import retrieve_user_info_tool

from app.core.prompt import ROOT_AGENT_INSTR

# carregar variáveis de ambiente
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
ADK_APP_NAME = os.getenv("ADK_APP_NAME", "nutriXpert")
ADK_MODEL = os.getenv("ADK_MODEL", "gemini-2.0-flash")
ADK_SERIALIZE_RUNNER = os.getenv("ADK_SERIALIZE_RUNNER", "false").lower() in ("1", "true", "yes")
AGENT_OUTPUT_KEY = "answer"


def build_agent() -> Agent:
    """
    Constrói um Agent.
    """
    return Agent(
        name="nutriXpert",
        model=ADK_MODEL,     #LiteLlm(model="ollama_chat/medgemma-4b"), utilizar este para rodar o medgemma local, precisa rodar o ollama e colocar o nome que voce usou
        instruction=ROOT_AGENT_INSTR,
        output_key=AGENT_OUTPUT_KEY,
        tools=[retrieve_user_info_tool],
        include_contents="default"

    )


async def create_runner():
    """
    Cria e retorna um runner + session_service já configurados.
    """
    session_service = DatabaseSessionService(DATABASE_URL)
    agent = build_agent()
    runner = Runner(agent=agent, app_name=ADK_APP_NAME, session_service=session_service)

    runner_lock = asyncio.Lock() if ADK_SERIALIZE_RUNNER else None

    return runner, session_service, runner_lock, ADK_APP_NAME, DATABASE_URL, AGENT_OUTPUT_KEY

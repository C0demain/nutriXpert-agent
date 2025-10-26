import asyncio
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from nutrixpert.agent import build_root_agent
from nutrixpert.api.routes import router as api_router
from nutrixpert.core.utils.constants import ADK_APP_NAME, ADK_SERIALIZE_RUNNER, AGENT_OUTPUT_KEY, DATABASE_URL
from nutrixpert.rag.rag_service import ingest_documents, build_vectorstore, CHROMA_PATH
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from nutrixpert.db import Base, engine

from nutrixpert.core.tools.retrieve_context import get_vectorstore

Base.metadata.create_all(bind=engine)

app = FastAPI(title="nutrixpert")

origins = [
    "http://localhost:8080", # Spring Boot API
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def create_runner():
    """
    Cria e retorna um runner + session_service já configurados.
    """
    session_service = DatabaseSessionService(DATABASE_URL)
    agent = build_root_agent()
    runner = Runner(agent=agent, app_name=ADK_APP_NAME, session_service=session_service)

    runner_lock = asyncio.Lock() if ADK_SERIALIZE_RUNNER else None

    return runner, session_service, runner_lock, ADK_APP_NAME, DATABASE_URL, AGENT_OUTPUT_KEY


@app.on_event("startup")
async def startup_event():
    # --- Ingestão inicial ---
    if not os.path.exists(CHROMA_PATH):
        print("🔍 Nenhum banco vetorial encontrado. Iniciando ingestão dos documentos...")
        docs = ingest_documents("documents")
        if not docs:
            print("⚠️ Nenhum documento encontrado em 'documents/'. O agente funcionará sem contexto externo.")
        else:
            build_vectorstore(docs)
            print(f"✅ Ingestão concluída. {len(docs)} documentos processados e armazenados em {CHROMA_PATH}")
    else:
        print(f"📂 Banco vetorial já existe em '{CHROMA_PATH}', pulando ingestão.")

    # --- Inicialização do ADK Runner ---
    runner, session_service, runner_lock, app_name, db_url, agent_output_key = await create_runner()

    app.state.runner = runner
    app.state.session_service = session_service
    app.state.runner_lock = runner_lock
    app.state.app_name = app_name
    app.state.db_url = db_url
    app.state.agent_output_key = agent_output_key
    app.state.vectordb = get_vectorstore()

    print("🤖 ADK runner criado e pronto.")
    print(f"   DB_URI: {db_url}")
    print(f"   App Name: {app_name}")


@app.on_event("shutdown")
async def shutdown_event():
    print("🔻 Shutdown - limpando recursos ADK (se necessário)")

# inclui rotas separadas
app.include_router(api_router)

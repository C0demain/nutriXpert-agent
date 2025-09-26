import asyncio
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.agent import create_runner
from app.api.routes import router as api_router
from app.rag.rag_service import ingest_documents, build_vectorstore, get_vectorstore, CHROMA_PATH

app = FastAPI(title="nutriXpert")

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

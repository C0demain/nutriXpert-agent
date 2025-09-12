import asyncio
from fastapi import FastAPI
from agent import create_runner
from routes import router as api_router

app = FastAPI(title="nutriXpert")

@app.on_event("startup")
async def startup_event():
    runner, session_service, runner_lock, app_name, db_url, agent_output_key = await create_runner()

    app.state.runner = runner
    app.state.session_service = session_service
    app.state.runner_lock = runner_lock
    app.state.app_name = app_name
    app.state.db_url = db_url
    app.state.agent_output_key = agent_output_key

    print("ADK runner criado e pronto. DB_URI:", db_url, "app_name:", app_name)


@app.on_event("shutdown")
async def shutdown_event():
    print("Shutdown - limpando recursos ADK (se necessário)")


# inclui rotas separadas
app.include_router(api_router)

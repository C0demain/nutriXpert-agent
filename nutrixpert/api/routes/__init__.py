from fastapi import APIRouter
from nutrixpert.api.routes.run_agent import router as run_agent_router
from nutrixpert.api.routes.get_session_history import router as get_session_router
from nutrixpert.api.routes.list_user_sessions import router as list_sessions_router

router = APIRouter()
router.include_router(run_agent_router)
router.include_router(get_session_router)
router.include_router(list_sessions_router)

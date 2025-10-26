from fastapi import APIRouter
from .agent_routes import router as agent_router
from .feedback_routes import router as feedback_router
from .session_routes import router as session_router

router = APIRouter()

router.include_router(agent_router, prefix="", tags=["Agent"])
router.include_router(feedback_router, prefix="", tags=["Feedback"])
router.include_router(session_router, prefix="", tags=["Sessions"])

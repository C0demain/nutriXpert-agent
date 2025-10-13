from typing import Optional
from pydantic import BaseModel

class AgentRequest(BaseModel):
    user_id: str
    session_id: str
    question: str
    app_name: Optional[str] = None

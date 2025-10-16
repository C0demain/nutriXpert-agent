from pydantic import BaseModel

class AgentRequest(BaseModel):
    user_id: str
    session_id: str
    question: str
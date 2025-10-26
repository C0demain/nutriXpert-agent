from pydantic import BaseModel
from typing import Optional

class SessionMessage(BaseModel):
    id: str
    timestamp: float
    author: str
    role: Optional[str] = None
    text: Optional[str] = None

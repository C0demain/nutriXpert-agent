from pydantic import BaseModel
from typing import Optional

class SessionListItem(BaseModel):
    session_id: str
    first_message: Optional[str] = None

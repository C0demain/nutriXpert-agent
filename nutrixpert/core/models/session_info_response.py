from pydantic import BaseModel
from typing import Optional, List
from nutrixpert.core.models.session_message import SessionMessage

class SessionInfoResponse(BaseModel):
    app_name: str
    user_id: str
    session_id: str
    create_time: Optional[str] = None
    update_time: Optional[str] = None
    state: Optional[dict] = None
    messages: List[SessionMessage] = []
    events: Optional[list] = None

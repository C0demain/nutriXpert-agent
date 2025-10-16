from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from nutrixpert.core.schemas.session_message import SessionMessage

class SessionInfoResponse(BaseModel):
    app_name: str
    user_id: str
    session_id: str
    create_time: Optional[str] = None
    update_time: Optional[str] = None
    state: Optional[Dict[str, Any]] = None
    messages: List[SessionMessage] = []
    events: Optional[list] = None

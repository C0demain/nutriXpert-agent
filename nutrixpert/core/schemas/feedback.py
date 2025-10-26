from pydantic import BaseModel, Field
from typing import Optional

class FeedbackCreate(BaseModel):
    message_id: str = Field(..., description="ID da resposta para associar o feedback")
    user_id: Optional[str] = Field(None, description="ID do usuário (opcional)")
    nota: int = Field(..., ge=0, le=5, description="Nota de 0 a 5")
    atendeu_expectativas: bool = Field(..., description="Se a resposta atendeu as expectativas")
    comentario: Optional[str] = Field(None, description="Comentário opcional do usuário")

class FeedbackResponse(BaseModel):
    id: int
    message_id: str
    user_id: Optional[str]
    nota: int
    atendeu_expectativas: bool
    comentario: Optional[str]

    class Config:
        orm_mode = True

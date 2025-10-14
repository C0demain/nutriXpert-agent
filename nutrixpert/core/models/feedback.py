from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from nutrixpert.db import Base  # usa o Base existente no projeto

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(64), nullable=False)
    user_id = Column(String(64), nullable=True)
    nota = Column(Integer, nullable=False)
    atendeu_expectativas = Column(Boolean, nullable=False)
    comentario = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

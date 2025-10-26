from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from nutrixpert.core.models.feedback import Feedback
from nutrixpert.core.schemas.feedback import FeedbackCreate, FeedbackResponse
from nutrixpert.core.tools.feedback_memory import add_feedback_to_memory
from nutrixpert.db import get_db

router = APIRouter()

@router.post("/feedback", response_model=FeedbackResponse)
def create_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    """
    Cria um novo feedback para uma resposta do agente.
    """
    existing = db.query(Feedback).filter(
        Feedback.message_id == feedback.message_id,
        Feedback.user_id == feedback.user_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Já existe um feedback para esta resposta (message_id={feedback.message_id})."
        )

    new_feedback = Feedback(
        message_id=feedback.message_id,
        user_id=feedback.user_id,
        nota=feedback.nota,
        atendeu_expectativas=feedback.atendeu_expectativas,
        comentario=feedback.comentario
    )

    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)

    if new_feedback.comentario:
        add_feedback_to_memory(
            feedback_id=new_feedback.id,
            comentario=new_feedback.comentario,
            nota=new_feedback.nota,
            user_id=new_feedback.user_id
        )

    return new_feedback

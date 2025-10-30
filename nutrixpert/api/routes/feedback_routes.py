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
        session_id=feedback.session_id,
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

@router.get("/feedback/conversa/{user_id}/{session_id}", response_model=list[FeedbackResponse])
def get_feedbacks_by_conversation(user_id: str, session_id: str, db: Session = Depends(get_db)):
    """
    Retorna todos os feedbacks de uma conversa específica de um usuário com o agente.
    """
    feedbacks = db.query(Feedback).filter(
        Feedback.user_id == user_id,
        Feedback.session_id == session_id
    ).all()

    if not feedbacks:
        raise HTTPException(status_code=404, detail="Nenhum feedback encontrado para esta conversa.")

    return feedbacks

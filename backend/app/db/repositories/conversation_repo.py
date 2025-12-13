"""Conversation repository."""
from sqlalchemy.orm import Session
from app.db.models import Conversation
import uuid


def get_or_create_conversation(db: Session, conversation_id: str = None) -> Conversation:
    """Get existing conversation or create new one."""
    if conversation_id:
        conv = db.query(Conversation).filter(Conversation.conversation_id == conversation_id).first()
        if conv:
            return conv
    
    # Create new conversation
    new_id = conversation_id or str(uuid.uuid4())
    conv = Conversation(conversation_id=new_id, status="active")
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


def update_conversation(db: Session, conversation_id: str, **kwargs) -> Conversation:
    """Update conversation fields."""
    conv = db.query(Conversation).filter(Conversation.conversation_id == conversation_id).first()
    if conv:
        for key, value in kwargs.items():
            setattr(conv, key, value)
        db.commit()
        db.refresh(conv)
    return conv



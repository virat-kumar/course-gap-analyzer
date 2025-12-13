"""Chat message repository."""
from sqlalchemy.orm import Session
from app.db.models import ChatMessage
from typing import List, Dict, Any


def create_chat_message(
    db: Session, 
    conversation_id: str, 
    role: str, 
    content: str, 
    metadata: Dict[str, Any] = None
) -> ChatMessage:
    """Create a new chat message."""
    message = ChatMessage(
        conversation_id=conversation_id,
        role=role,
        content=content,
        metadata_json=metadata or {}
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_conversation_messages(db: Session, conversation_id: str, limit: int = 50) -> List[ChatMessage]:
    """Get conversation history, most recent first."""
    return db.query(ChatMessage)\
        .filter(ChatMessage.conversation_id == conversation_id)\
        .order_by(ChatMessage.created_at.asc())\
        .limit(limit)\
        .all()


def get_conversation_messages_for_llm(db: Session, conversation_id: str, limit: int = 20) -> List[Dict[str, str]]:
    """Get conversation messages formatted for LLM (list of dicts with role and content)."""
    messages = get_conversation_messages(db, conversation_id, limit)
    return [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]




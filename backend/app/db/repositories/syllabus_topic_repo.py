"""Syllabus topic repository."""
from sqlalchemy.orm import Session
from app.db.models import SyllabusTopic
from typing import List


def get_topics_by_document_id(db: Session, document_id: str) -> List[SyllabusTopic]:
    """Get all syllabus topics for a document."""
    return db.query(SyllabusTopic).filter(SyllabusTopic.document_id == document_id).all()


def create_topic(db: Session, topic: SyllabusTopic) -> SyllabusTopic:
    """Create a new syllabus topic."""
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic



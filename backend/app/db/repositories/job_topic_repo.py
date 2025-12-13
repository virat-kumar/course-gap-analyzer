"""Job topic repository."""
from sqlalchemy.orm import Session
from app.db.models import JobTopic
from typing import List


def get_topics_by_conversation(db: Session, conversation_id: str) -> List[JobTopic]:
    """Get all job topics for a conversation."""
    return db.query(JobTopic).filter(JobTopic.conversation_id == conversation_id).all()


def create_job_topic(db: Session, topic: JobTopic) -> JobTopic:
    """Create a new job topic."""
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic



"""Job source repository."""
from sqlalchemy.orm import Session
from app.db.models import JobSource
from typing import List, Optional


def get_sources_by_conversation(db: Session, conversation_id: str) -> List[JobSource]:
    """Get all job sources for a conversation."""
    return db.query(JobSource).filter(JobSource.conversation_id == conversation_id).all()


def get_source_by_hash(db: Session, content_hash: str) -> Optional[JobSource]:
    """Get job source by content hash (for deduplication)."""
    return db.query(JobSource).filter(JobSource.content_hash == content_hash).first()


def create_job_source(db: Session, job_source: JobSource) -> JobSource:
    """Create a new job source."""
    db.add(job_source)
    db.commit()
    db.refresh(job_source)
    return job_source



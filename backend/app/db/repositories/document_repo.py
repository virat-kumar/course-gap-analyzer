"""Document repository."""
from sqlalchemy.orm import Session
from app.db.models import Document


def get_document_by_id(db: Session, document_id: str) -> Document:
    """Get document by ID."""
    return db.query(Document).filter(Document.document_id == document_id).first()


def create_document(db: Session, document: Document) -> Document:
    """Create a new document."""
    db.add(document)
    db.commit()
    db.refresh(document)
    return document



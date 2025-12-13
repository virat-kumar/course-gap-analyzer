"""PDF-related schemas."""
from pydantic import BaseModel, Field


class PDFResponse(BaseModel):
    """Response schema for /pdf endpoint."""
    document_id: str = Field(..., description="Unique document ID")
    extracted_text_preview: str = Field(..., description="Preview of extracted text (first 500 chars)")
    topic_extract_status: str = Field(..., description="Status of topic extraction: 'pending', 'completed', 'failed'")



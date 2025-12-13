"""PDF upload and processing routes."""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.pdf_service import process_pdf
from app.schemas.pdf import PDFResponse
from typing import Annotated

router = APIRouter(prefix="/pdf", tags=["pdf"])


@router.post("", response_model=PDFResponse)
async def upload_pdf(
    file: Annotated[UploadFile, File()],
    db: Session = Depends(get_db)
):
    """
    Upload and process PDF syllabus.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        pdf_bytes = await file.read()
        
        document_id, text_preview, topic_extract_status = process_pdf(
            pdf_bytes, file.filename, db
        )
        
        return PDFResponse(
            document_id=document_id,
            extracted_text_preview=text_preview,
            topic_extract_status=topic_extract_status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")



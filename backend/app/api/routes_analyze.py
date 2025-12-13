"""Analysis routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.analyze_service import generate_tables, store_analysis
from app.services.chat_service import handle_analyze
from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.post("", response_model=AnalyzeResponse)
async def analyze_gaps(
    analyze_req: AnalyzeRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze gaps between syllabus and industry job descriptions.
    """
    try:
        return handle_analyze(analyze_req, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing: {str(e)}")



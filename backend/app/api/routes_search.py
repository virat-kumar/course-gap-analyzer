"""Search routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.search_service import handle_search
from app.services.chat_service import handle_search as chat_search_handler
from app.schemas.search import SearchRequest, SearchResponse

router = APIRouter(prefix="/search", tags=["search"])


@router.post("", response_model=SearchResponse)
async def search_jobs(
    search_req: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search for job descriptions based on constraints.
    """
    try:
        return handle_search(search_req, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching: {str(e)}")



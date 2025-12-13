"""Chat routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.chat_service import handle_chat_message
from app.schemas.chat import ChatRequest, ChatResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    chat_req: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Chat endpoint - tool-using agent.
    """
    try:
        result = handle_chat_message(
            chat_req.message,
            chat_req.conversation_id,
            chat_req.document_id,
            db
        )
        
        # Final commit to ensure all messages are saved
        try:
            db.commit()
        except Exception as commit_error:
            logger.error(f"Error in final commit: {commit_error}")
            db.rollback()
        
        return ChatResponse(
            response=result["response"],
            conversation_id=result["conversation_id"],
            tool_calls=result.get("tool_calls"),
            tables=result.get("tables")
        )
    except Exception as e:
        # Rollback on error
        db.rollback()
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error in chat: {str(e)}")



"""Chat-related schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ChatRequest(BaseModel):
    """Request schema for /chat endpoint."""
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID")
    message: str = Field(..., description="User chat message")
    document_id: Optional[str] = Field(None, description="Optional document ID to reference")


class ChatResponse(BaseModel):
    """Response schema for /chat endpoint."""
    response: str = Field(..., description="Assistant response text")
    conversation_id: str = Field(..., description="Conversation ID")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(None, description="Tool calls made by agent")
    tables: Optional[Dict[str, Any]] = Field(None, description="Tables if analysis was performed")



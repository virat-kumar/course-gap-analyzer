"""Chat service with tool-using agent and multi-turn conversation support."""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.services.search_service import parse_constraints, collect_sources, verify_and_store
from app.services.analyze_service import generate_tables, store_analysis
from app.schemas.search import SearchRequest, SearchResponse
from app.schemas.analyze import AnalyzeRequest
from app.db.repositories.conversation_repo import get_or_create_conversation
from app.db.repositories.chat_message_repo import (
    create_chat_message, 
    get_conversation_messages_for_llm
)
from app.db.session import SessionLocal
from app.core.config import settings
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from prompts.prompts import CHAT_SYSTEM_PROMPT
import logging

logger = logging.getLogger(__name__)


def get_llm_client():
    """Get Azure OpenAI LLM client."""
    return AzureChatOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version=settings.api_version,
        azure_deployment=settings.azure_openai_model,
        temperature=0.7,
    )


def handle_chat_message(message: str, conversation_id: Optional[str], document_id: Optional[str], db: Session) -> Dict[str, Any]:
    """
    Handle chat message with multi-turn conversation support.
    Maintains context and can call tools (search/analyze) when needed.
    """
    message_lower = message.lower()
    
    # Get or create conversation
    conv = get_or_create_conversation(db, conversation_id)
    conversation_id = conv.conversation_id
    
    response = {
        "response": "",
        "conversation_id": conversation_id,
        "tool_calls": None,
        "tables": None
    }
    
    # Get conversation history (before storing current message)
    history = get_conversation_messages_for_llm(db, conversation_id, limit=20)
    
    # Store user message directly in main session
    try:
        from app.db.models import ChatMessage
        user_msg = ChatMessage(
            conversation_id=conversation_id,
            role="user",
            content=message,
            metadata_json={}
        )
        db.add(user_msg)
        db.commit()
        db.refresh(user_msg)
        logger.info(f"Stored user message ID {user_msg.id} for conversation {conversation_id[:8]}...")
    except Exception as e:
        logger.error(f"Error storing user message: {e}", exc_info=True)
        db.rollback()
    
    # Check if user wants to search (more flexible matching)
    has_search_verb = "find" in message_lower or "search" in message_lower or "look for" in message_lower
    has_job_term = "job" in message_lower or "position" in message_lower or "role" in message_lower or "hiring" in message_lower or "career" in message_lower
    is_search_request = has_search_verb and has_job_term
    
    if is_search_request:
        # Call search
        search_req = SearchRequest(instruction=message, conversation_id=conversation_id)
        search_result = handle_search(search_req, db)
        response_text = f"I found {search_result.results_count} job descriptions. You can now ask me to analyze the syllabus against these jobs."
        response["response"] = response_text
        response["tool_calls"] = [{"tool": "search", "status": "completed"}]
        
        # Store assistant response
        try:
            from app.db.models import ChatMessage
            assistant_msg = ChatMessage(
                conversation_id=conversation_id,
                role="assistant",
                content=response_text,
                metadata_json={"tool_calls": response["tool_calls"]}
            )
            db.add(assistant_msg)
            db.commit()
            db.refresh(assistant_msg)
            logger.info(f"Stored assistant message (search) ID {assistant_msg.id} for conversation {conversation_id[:8]}...")
        except Exception as e:
            logger.error(f"Error storing assistant message: {e}", exc_info=True)
            db.rollback()
        return response
    
    # Check if user wants analysis
    if any(keyword in message_lower for keyword in ["analyze", "analysis", "gap", "compare", "missing"]):
        if not document_id:
            response_text = "Please provide a document_id to analyze."
            response["response"] = response_text
            try:
                from app.db.models import ChatMessage
                assistant_msg = ChatMessage(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=response_text,
                    metadata_json={}
                )
                db.add(assistant_msg)
                db.commit()
                db.refresh(assistant_msg)
            except Exception as e:
                logger.error(f"Error storing assistant message: {e}", exc_info=True)
                db.rollback()
            return response
        
        # Call analyze
        analyze_req = AnalyzeRequest(conversation_id=conversation_id, document_id=document_id)
        analyze_result = handle_analyze(analyze_req, db)
        
        response_text = "Analysis complete! Here are the results:"
        response["response"] = response_text
        response["tool_calls"] = [{"tool": "analyze", "status": "completed"}]
        response["tables"] = {
            "table_a": [row.model_dump() for row in analyze_result.table_a],
            "table_b": [row.model_dump() for row in analyze_result.table_b]
        }
        
        # Store assistant response
        try:
            from app.db.models import ChatMessage
            assistant_msg = ChatMessage(
                conversation_id=conversation_id,
                role="assistant",
                content=response_text,
                metadata_json={"tool_calls": response["tool_calls"], "tables": response["tables"]}
            )
            db.add(assistant_msg)
            db.commit()
            db.refresh(assistant_msg)
            logger.info(f"Stored assistant message (analyze) ID {assistant_msg.id} for conversation {conversation_id[:8]}...")
        except Exception as e:
            logger.error(f"Error storing assistant message: {e}", exc_info=True)
            db.rollback()
        return response
    
    # Use LLM for general conversation with history
    try:
        llm = get_llm_client()
        
        # Build messages for LLM using langchain message format
        langchain_messages = [SystemMessage(content=CHAT_SYSTEM_PROMPT)]
        
        # Convert history to langchain messages
        for hist_msg in history:
            if hist_msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=hist_msg["content"]))
            elif hist_msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=hist_msg["content"]))
        
        # Add current user message
        langchain_messages.append(HumanMessage(content=message))
        
        logger.info(f"Calling LLM with {len(langchain_messages)} messages (history: {len(history)})")
        
        # Get response from LLM
        llm_response = llm.invoke(langchain_messages)
        response_text = llm_response.content
        
        logger.info(f"LLM response received: {len(response_text)} chars")
        
        response["response"] = response_text
        
        # Store assistant response
        try:
            from app.db.models import ChatMessage
            assistant_msg = ChatMessage(
                conversation_id=conversation_id,
                role="assistant",
                content=response_text,
                metadata_json={}
            )
            db.add(assistant_msg)
            db.commit()
            db.refresh(assistant_msg)
            logger.info(f"Stored assistant message (LLM) ID {assistant_msg.id} for conversation {conversation_id[:8]}...")
        except Exception as e:
            logger.error(f"Error storing assistant message: {e}", exc_info=True)
            db.rollback()
        
    except Exception as e:
        logger.error(f"Error in LLM chat: {str(e)}", exc_info=True)
        import traceback
        logger.error(traceback.format_exc())
        # Fallback response
        response_text = "I can help you:\n1. Search for job descriptions\n2. Analyze syllabus gaps\n\nWhat would you like to do?"
        response["response"] = response_text
        try:
            from app.db.models import ChatMessage
            assistant_msg = ChatMessage(
                conversation_id=conversation_id,
                role="assistant",
                content=response_text,
                metadata_json={}
            )
            db.add(assistant_msg)
            db.commit()
            db.refresh(assistant_msg)
            logger.info(f"Stored assistant message (fallback) ID {assistant_msg.id} for conversation {conversation_id[:8]}...")
        except Exception as e2:
            logger.error(f"Error storing fallback message: {e2}", exc_info=True)
            db.rollback()
    
    return response


def handle_search(search_req: SearchRequest, db: Session) -> SearchResponse:
    """Handle search request."""
    # Parse constraints
    parsed = parse_constraints(search_req.instruction)
    
    # Get or create conversation
    conv = get_or_create_conversation(db, search_req.conversation_id)
    conversation_id = conv.conversation_id
    
    # Collect sources
    sources = collect_sources(parsed, db, conversation_id)
    
    # Verify and store
    verified, count = verify_and_store(sources, parsed, db, conversation_id)
    
    # Update conversation
    from app.db.repositories.conversation_repo import update_conversation
    update_conversation(db, conversation_id, parsed_constraints_json=parsed.model_dump(), status="search_completed")
    
    return SearchResponse(
        conversation_id=conversation_id,
        parsed_constraints=parsed,
        verified=verified,
        results_count=count,
        sources_sample=[{"url": s.url, "title": s.title} for s in sources[:3]]
    )


def handle_analyze(analyze_req: AnalyzeRequest, db: Session):
    """Handle analyze request."""
    from app.schemas.analyze import AnalyzeResponse, TableARow, TableBRow
    
    # Generate tables
    tables = generate_tables(analyze_req.document_id, analyze_req.conversation_id, db)
    
    # Store analysis
    store_analysis(analyze_req.document_id, analyze_req.conversation_id, tables, db)
    
    # Convert to response format
    table_a = [TableARow(**row) for row in tables.get("table_a", [])]
    table_b = [TableBRow(**row) for row in tables.get("table_b", [])]
    
    return AnalyzeResponse(
        table_a=table_a,
        table_b=table_b,
        analysis_metadata={"status": "completed"}
    )


"""PDF processing service."""
import uuid
from pathlib import Path
from typing import Tuple
from sqlalchemy.orm import Session
from app.tools.pdf_extract_tool import extract_text_from_bytes
from app.utils.security import sanitize_text
from prompts.prompts import SYLLABUS_TOPIC_EXTRACT_PROMPT
from app.core.config import settings
from langchain_openai import AzureChatOpenAI
import json
from app.db.models import Document, SyllabusTopic


def get_llm_client():
    """Get Azure OpenAI LLM client."""
    return AzureChatOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version=settings.api_version,
        azure_deployment=settings.azure_openai_model,
        temperature=0.1,
    )


def extract_text(pdf_bytes: bytes) -> Tuple[str, bool]:
    """
    Extract text from PDF bytes.
    
    Args:
        pdf_bytes: PDF file content as bytes
        
    Returns:
        Tuple of (extracted_text, ocr_used)
    """
    return extract_text_from_bytes(pdf_bytes)


def extract_topics(text: str, db: Session) -> list:
    """
    Extract topics from syllabus text using LLM.
    
    Args:
        text: Extracted syllabus text
        db: Database session
        
    Returns:
        List of extracted topics
    """
    # Sanitize text first
    sanitized_text = sanitize_text(text)
    
    # Prepare prompt - use replace instead of format to avoid issues with JSON braces in prompt
    prompt = SYLLABUS_TOPIC_EXTRACT_PROMPT.replace("{syllabus_text}", sanitized_text[:20000])  # Limit text length
    
    # Call LLM
    llm = get_llm_client()
    
    try:
        response = llm.invoke(prompt)
        response_text = response.content
        
        # Parse JSON from response
        # Try to extract JSON from markdown code blocks if present
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        
        # Try to find JSON array in the text
        # Look for opening bracket
        start_idx = response_text.find('[')
        if start_idx == -1:
            print(f"No JSON array found in response: {response_text[:200]}")
            return []
        
        # Find matching closing bracket
        bracket_count = 0
        end_idx = start_idx
        for i in range(start_idx, len(response_text)):
            if response_text[i] == '[':
                bracket_count += 1
            elif response_text[i] == ']':
                bracket_count -= 1
                if bracket_count == 0:
                    end_idx = i + 1
                    break
        
        if end_idx <= start_idx:
            print(f"Could not find matching closing bracket")
            return []
        
        json_str = response_text[start_idx:end_idx]
        topics = json.loads(json_str)
        
        if not isinstance(topics, list):
            topics = []
            
        return topics
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error extracting topics: {str(e)}")
        print(f"Response text (first 500 chars): {response_text[:500] if 'response_text' in locals() else 'N/A'}")
        return []
    except Exception as e:
        print(f"Error extracting topics: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def process_pdf(pdf_bytes: bytes, filename: str, db: Session) -> Tuple[str, str, str]:
    """
    Process uploaded PDF: extract text and topics, store in DB.
    
    Args:
        pdf_bytes: PDF file content
        filename: Original filename
        db: Database session
        
    Returns:
        Tuple of (document_id, text_preview, topic_extract_status)
    """
    try:
        # Extract text
        raw_text, ocr_used = extract_text(pdf_bytes)
        
        # Create document record
        document_id = str(uuid.uuid4())
        document = Document(
            document_id=document_id,
            filename=filename,
            raw_text=raw_text,
            extraction_method="pdfplumber",
            ocr_used=ocr_used
        )
        db.add(document)
        db.flush()  # Get document_id
        
        # Extract topics
        topics = extract_topics(raw_text, db)
        topic_extract_status = "completed" if topics else "failed"
        
        # Store topics
        for idx, topic_data in enumerate(topics):
            try:
                if isinstance(topic_data, dict):
                    topic_name = topic_data.get("topic_name") or topic_data.get("topic") or ""
                    if not topic_name:
                        print(f"Warning: Topic {idx} has no topic_name")
                        continue
                    topic = SyllabusTopic(
                        document_id=document_id,
                        topic_name=str(topic_name),
                        module=topic_data.get("module"),
                        keywords_json=topic_data.get("keywords", []),
                        confidence=float(topic_data.get("confidence", 0.0))
                    )
                    db.add(topic)
                elif isinstance(topic_data, str):
                    # Handle case where LLM returns simple string list
                    topic = SyllabusTopic(
                        document_id=document_id,
                        topic_name=str(topic_data),
                        module=None,
                        keywords_json=[],
                        confidence=0.8
                    )
                    db.add(topic)
            except Exception as e:
                print(f"Error storing topic {idx} ({type(topic_data)}): {str(e)}")
                import traceback
                traceback.print_exc()
                continue
        
        db.commit()
        
        # Return preview (first 500 chars)
        text_preview = raw_text[:500] if raw_text else ""
        
        return document_id, text_preview, topic_extract_status
    except Exception as e:
        db.rollback()
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in process_pdf: {str(e)}")
        print(error_details)
        raise


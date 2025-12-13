"""Search service for job descriptions."""
import uuid
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.schemas.search import ConstraintParsingOutput, TimeWindow
from app.agents.verify_agent import verify_evidence
from app.tools.web_search_tool import search_web
from app.tools.fetch_tool import fetch_web_page, extract_company_from_url
from prompts.prompts import CONSTRAINT_PARSING_PROMPT, JOB_TOPIC_EXTRACT_PROMPT, RETRY_QUERY_PROMPT
from app.core.config import settings
from langchain_openai import AzureChatOpenAI
from app.db.models import Conversation, JobSource, JobTopic
from app.db.repositories.conversation_repo import get_or_create_conversation
from app.db.repositories.job_source_repo import create_job_source, get_source_by_hash
from app.db.repositories.job_topic_repo import create_job_topic
from app.utils.text import normalize_topic
import time

# Setup logger
logger = logging.getLogger(__name__)


def get_llm_client():
    """Get Azure OpenAI LLM client."""
    return AzureChatOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version=settings.api_version,
        azure_deployment=settings.azure_openai_model,
        temperature=0.1,
    )


def parse_constraints(instruction: str) -> ConstraintParsingOutput:
    """Parse user instruction into structured constraints."""
    llm = get_llm_client()
    
    prompt = CONSTRAINT_PARSING_PROMPT.replace("{instruction}", instruction)
    
    try:
        response = llm.invoke(prompt)
        response_text = response.content
        
        # Extract JSON
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        
        constraints_dict = json.loads(response_text)
        return ConstraintParsingOutput(**constraints_dict)
        
    except Exception as e:
        print(f"Error parsing constraints: {str(e)}")
        # Return defaults
        return ConstraintParsingOutput(
            company_tier="any",
            role_keywords=[],
            time_window=None,
            location=None,
            company_allowlist=None,
            seniority=None,
            sources_preference=None
        )


def extract_job_topics(job_texts: List[str]) -> List[Dict[str, Any]]:
    """Extract topics from job description texts."""
    llm = get_llm_client()
    all_topics = []
    
    # Process in chunks
    for job_text in job_texts[:10]:  # Limit to avoid too many API calls
        prompt = JOB_TOPIC_EXTRACT_PROMPT.replace("{job_text}", job_text[:5000])
        
        try:
            response = llm.invoke(prompt)
            response_text = response.content
            
            # Extract JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            topics = json.loads(response_text)
            if isinstance(topics, list):
                all_topics.extend(topics)
                
        except Exception as e:
            print(f"Error extracting topics from job text: {str(e)}")
            continue
    
    return all_topics


def collect_sources(parsed_constraints: ConstraintParsingOutput, db: Session, conversation_id: str) -> List[JobSource]:
    """Collect job sources via web search."""
    # Build search query
    query_parts = []
    query_parts.extend(parsed_constraints.role_keywords)
    if parsed_constraints.location:
        query_parts.append(parsed_constraints.location)
    if parsed_constraints.company_tier == "top_companies":
        query_parts.append("top tech companies")
    
    query = " ".join(query_parts)
    query += " job description"
    
    # Search
    try:
        search_results = search_web(query, max_results=10)
    except ValueError as e:
        # Tavily API key not set
        print(f"Search error (API key not set): {str(e)}")
        return []
    except Exception as e:
        print(f"Search error: {str(e)}")
        return []
    
    collected_sources = []
    
    # Fetch pages
    for result in search_results:
        url = result.get("url", "")
        if not url:
            continue
        
        # Check for duplicates
        fetched = fetch_web_page(url)
        if fetched["status"] != "success":
            continue
        
        content_hash = fetched.get("content_hash")
        if content_hash:
            existing = get_source_by_hash(db, content_hash)
            if existing:
                collected_sources.append(existing)
                continue
        
        # Extract company name
        company = extract_company_from_url(url)
        if not company:
            company = result.get("title", "").split("-")[0].strip()
        
        # Create job source
        job_source = JobSource(
            conversation_id=conversation_id,
            url=url,
            source_site=result.get("source", "unknown"),
            title=result.get("title", fetched.get("title", "")),
            company=company,
            role=parsed_constraints.role_keywords[0] if parsed_constraints.role_keywords else None,
            snippet=fetched.get("snippet", result.get("content", "")[:500]),
            raw_text=fetched.get("raw_text", ""),
            access_status=fetched.get("status", "success"),
            content_hash=content_hash
        )
        
        job_source = create_job_source(db, job_source)
        collected_sources.append(job_source)
    
    return collected_sources


def verify_and_store(evidence: List[JobSource], constraints: ConstraintParsingOutput, db: Session, conversation_id: str) -> tuple[bool, int]:
    """Verify evidence and store job topics."""
    # Prepare evidence summary
    companies = list(set([s.company for s in evidence if s.company]))
    evidence_summary = {
        "job_count": len(evidence),
        "companies": companies,
        "date_range": "recent"  # Simplified
    }
    
    # Verify
    constraints_dict = constraints.model_dump()
    verifier_result = verify_evidence(constraints_dict, evidence_summary)
    
    # Always extract and store topics, even if verifier fails
    # (We'll still store them but mark verification status)
    
    # Extract topics from job descriptions
    stored_count = 0
    for job_source in evidence:
        if job_source.raw_text or job_source.snippet:
            job_text = job_source.raw_text or job_source.snippet
            if not job_text or len(job_text) < 50:  # Skip if too short
                continue
            
            # Extract topics for this specific job
            try:
                logger.info(f"Extracting topics from job source {job_source.id} (text length: {len(job_text)})")
                topics_for_job = extract_job_topics([job_text[:5000]])  # Limit text length
                logger.info(f"Got {len(topics_for_job)} topics from job source {job_source.id}")
                
                for topic_data in topics_for_job:
                    if isinstance(topic_data, dict):
                        topic_name = topic_data.get("topic") or topic_data.get("raw_topic", "")
                        if not topic_name or len(topic_name.strip()) == 0:
                            logger.warning(f"Skipping empty topic: {topic_data}")
                            continue
                        normalized = normalize_topic(topic_name)
                        if normalized and len(normalized) > 2:  # Valid topic
                            try:
                                job_topic = JobTopic(
                                    conversation_id=conversation_id,
                                    job_source_id=job_source.id,
                                    normalized_topic=normalized,
                                    raw_topic=topic_data.get("raw_topic", topic_name),
                                    frequency_weight=1.0,
                                    confidence=float(topic_data.get("confidence", 0.8))
                                )
                                create_job_topic(db, job_topic)
                                stored_count += 1
                                logger.debug(f"Stored topic: {normalized}")
                            except Exception as e:
                                logger.error(f"Error storing topic {normalized}: {e}", exc_info=True)
                        else:
                            logger.warning(f"Skipping invalid normalized topic: '{normalized}' (original: '{topic_name}')")
                    else:
                        logger.warning(f"Skipping non-dict topic data: {topic_data}")
            except Exception as e:
                logger.error(f"Error extracting topics from job {job_source.id}: {str(e)}", exc_info=True)
                continue
    
    logger.info(f"Stored {stored_count} job topics from {len(evidence)} job sources")
    
    # Commit all changes
    db.commit()
    
    # Return verification status and topic count
    return verifier_result.is_passed, stored_count


def handle_search(search_req: SearchRequest, db: Session) -> SearchResponse:
    """Handle search request - main entry point."""
    # Parse constraints
    parsed = parse_constraints(search_req.instruction)
    
    # Get or create conversation
    from app.db.repositories.conversation_repo import get_or_create_conversation, update_conversation
    conv = get_or_create_conversation(db, search_req.conversation_id)
    conversation_id = conv.conversation_id
    
    # Collect sources
    sources = collect_sources(parsed, db, conversation_id)
    
    # Verify and store
    verified, topics_stored = verify_and_store(sources, parsed, db, conversation_id)
    
    # Update conversation
    update_conversation(db, conversation_id, parsed_constraints_json=parsed.model_dump(), status="search_completed")
    
    # Verify topics were actually stored
    from app.db.repositories.job_topic_repo import get_topics_by_conversation
    stored_topics = get_topics_by_conversation(db, conversation_id)
    logger.info(f"Search completed: {len(sources)} sources, {len(stored_topics)} topics stored")
    
    return SearchResponse(
        conversation_id=conversation_id,
        parsed_constraints=parsed,
        verified=verified,
        results_count=len(sources),  # Return source count, not topic count
        sources_sample=[{"url": s.url, "title": s.title} for s in sources[:3]]
    )


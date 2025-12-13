"""Analysis service for generating gap analysis tables."""
import json
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.db.models import SyllabusTopic, JobTopic, AnalysisRun, AnalysisTableARow, AnalysisTableBRow
from app.db.repositories.syllabus_topic_repo import get_topics_by_document_id
from app.db.repositories.job_topic_repo import get_topics_by_conversation as get_job_topics_by_conversation_id
from app.db.repositories.analysis_repo import (
    create_analysis_run, create_table_a_row, create_table_b_row, get_table_a_rows, get_table_b_rows
)
from prompts.prompts import ANALYSIS_PROMPT
from app.core.config import settings
from langchain_openai import AzureChatOpenAI
from datetime import datetime


def get_llm_client():
    """Get Azure OpenAI LLM client."""
    return AzureChatOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version=settings.api_version,
        azure_deployment=settings.azure_openai_model,
        temperature=0.1,
    )


def generate_tables(document_id: str, conversation_id: str, db: Session) -> Dict[str, Any]:
    """Generate Table A and Table B."""
    # Load syllabus topics
    syllabus_topics = get_topics_by_document_id(db, document_id)
    syllabus_list = [t.topic_name for t in syllabus_topics]
    
    # Load job topics
    job_topics = get_job_topics_by_conversation_id(db, conversation_id)
    
    # Get unique normalized topics with frequency
    topic_freq = {}
    for job_topic in job_topics:
        normalized = job_topic.normalized_topic
        topic_freq[normalized] = topic_freq.get(normalized, 0) + 1
    
    job_topics_list = list(topic_freq.keys())
    
    # Get job source URLs for references
    from app.db.repositories.job_source_repo import get_sources_by_conversation
    job_sources = get_sources_by_conversation(db, conversation_id)
    job_urls = [s.url for s in job_sources]
    
    # Prepare prompt
    syllabus_topics_str = json.dumps(syllabus_list, indent=2)
    job_topics_str = json.dumps(list(topic_freq.items())[:50], indent=2)  # Limit to top 50
    urls_str = json.dumps(job_urls[:20], indent=2)  # Limit URLs
    
    prompt = ANALYSIS_PROMPT.replace("{syllabus_topics}", syllabus_topics_str).replace("{job_topics}", job_topics_str).replace("{job_source_urls}", urls_str)
    
    # Call LLM
    llm = get_llm_client()
    
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
        
        result = json.loads(response_text)
        
        return {
            "table_a": result.get("table_a", []),
            "table_b": result.get("table_b", [])
        }
        
    except Exception as e:
        print(f"Error generating tables: {str(e)}")
        return {"table_a": [], "table_b": []}


def store_analysis(document_id: str, conversation_id: str, tables: Dict[str, Any], db: Session) -> int:
    """Store analysis results in database."""
    # Create analysis run
    analysis_run = AnalysisRun(
        conversation_id=conversation_id,
        document_id=document_id,
        model_version=settings.azure_openai_model,
        prompt_version="1.0",
        tool_versions={"langchain": "1.1.3"}
    )
    analysis_run = create_analysis_run(db, analysis_run)
    
    # Store Table A rows
    for row_data in tables.get("table_a", []):
        row = AnalysisTableARow(
            analysis_run_id=analysis_run.id,
            syllabus_topic=row_data.get("syllabus_topic", ""),
            industry_relevance_score=row_data.get("industry_relevance_score", 0),
            evidence_job_count=row_data.get("evidence_job_count", 0),
            example_industry_phrasing=row_data.get("example_industry_phrasing", ""),
            notes=row_data.get("notes"),
            references_json=row_data.get("references", [])
        )
        create_table_a_row(db, row)
    
    # Store Table B rows
    for row_data in tables.get("table_b", []):
        priority = row_data.get("priority", "Medium")
        row = AnalysisTableBRow(
            analysis_run_id=analysis_run.id,
            missing_topic=row_data.get("missing_topic", ""),
            frequency_in_jobs=row_data.get("frequency_in_jobs", 0),
            priority=priority,
            suggested_syllabus_insertion=row_data.get("suggested_syllabus_insertion", ""),
            rationale=row_data.get("rationale", ""),
            references_json=row_data.get("references", [])
        )
        create_table_b_row(db, row)
    
    return analysis_run.id


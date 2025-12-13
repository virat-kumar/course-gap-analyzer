"""Analysis-related schemas."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class Priority(str, Enum):
    """Priority levels for missing topics."""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class TableARow(BaseModel):
    """Row in Table A: Syllabus topics still viable in industry."""
    syllabus_topic: str = Field(..., description="Topic from syllabus")
    industry_relevance_score: int = Field(..., ge=0, le=100, description="Relevance score 0-100")
    evidence_job_count: int = Field(..., ge=0, description="Number of jobs mentioning this topic")
    example_industry_phrasing: str = Field(..., description="1-2 short phrases from industry")
    notes: Optional[str] = Field(None, description="Additional notes")
    references: List[str] = Field(default_factory=list, description="URLs from job_sources")


class TableBRow(BaseModel):
    """Row in Table B: Missing topics to add to syllabus."""
    missing_topic: str = Field(..., description="Topic missing from syllabus")
    frequency_in_jobs: int = Field(..., ge=0, description="Number of jobs mentioning this")
    priority: Priority = Field(..., description="Priority level")
    suggested_syllabus_insertion: str = Field(..., description="Where to add (e.g., 'Week 3', 'Module 2')")
    rationale: str = Field(..., description="Why this topic should be added")
    references: List[str] = Field(default_factory=list, description="URLs from job_sources")


class AnalyzeRequest(BaseModel):
    """Request schema for /analyze endpoint."""
    conversation_id: str = Field(..., description="Conversation ID with job search results")
    document_id: str = Field(..., description="Document ID of uploaded syllabus")


class AnalyzeResponse(BaseModel):
    """Response schema for /analyze endpoint."""
    table_a: List[TableARow] = Field(default_factory=list, description="Syllabus topics still viable")
    table_b: List[TableBRow] = Field(default_factory=list, description="Missing topics to add")
    analysis_metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata about analysis run")



"""Search-related schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class TimeWindow(BaseModel):
    """Time window specification."""
    unit: str = Field(..., description="Time unit: 'days', 'months', or 'years'")
    value: int = Field(..., ge=1, description="Numeric value")


class ConstraintParsingOutput(BaseModel):
    """Parsed search constraints from user instruction."""
    time_window: Optional[TimeWindow] = Field(None, description="Time window for job postings")
    role_keywords: List[str] = Field(default_factory=list, description="Job role keywords")
    location: Optional[str] = Field(None, description="Geographic location")
    company_tier: str = Field(..., description="Company tier: 'top_companies', 'any', or specific list")
    company_allowlist: Optional[List[str]] = Field(None, description="Specific companies to include")
    seniority: Optional[str] = Field(None, description="Seniority level: 'intern', 'entry', 'mid', 'senior'")
    sources_preference: Optional[List[str]] = Field(None, description="Preferred sources: 'greenhouse', 'lever', etc.")


class SearchRequest(BaseModel):
    """Request schema for /search endpoint."""
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID")
    instruction: str = Field(..., description="Natural language instruction for job search")


class SearchResponse(BaseModel):
    """Response schema for /search endpoint."""
    conversation_id: str = Field(..., description="Conversation ID")
    parsed_constraints: ConstraintParsingOutput = Field(..., description="Parsed constraints")
    verified: bool = Field(..., description="Whether evidence passed verification")
    results_count: int = Field(..., ge=0, description="Number of verified job sources")
    sources_sample: List[Dict[str, Any]] = Field(default_factory=list, description="Sample of collected sources")



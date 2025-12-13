"""Verifier agent output schemas."""
from pydantic import BaseModel, Field
from typing import List, Dict, Any


class VerifierOutput(BaseModel):
    """Output from verifier agent validating evidence against constraints."""
    is_passed: bool = Field(..., alias="pass", description="Whether evidence passes all constraints")
    fail_reasons: List[str] = Field(default_factory=list, description="List of failure reasons if pass=False")
    constraint_violations: Dict[str, str] = Field(default_factory=dict, description="Specific constraint violations")
    retry_query_suggestions: List[str] = Field(default_factory=list, description="Suggested query refinements for retry")
    coverage_score: int = Field(..., ge=0, le=100, description="How well results meet constraints (0-100)")


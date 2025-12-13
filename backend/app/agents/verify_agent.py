"""Verifier agent for validating evidence against constraints."""
from langchain_openai import AzureChatOpenAI
from prompts.prompts import VERIFIER_PROMPT
from app.core.config import settings
from app.schemas.verifier import VerifierOutput
import json


def get_llm_client():
    """Get Azure OpenAI LLM client."""
    return AzureChatOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version=settings.api_version,
        azure_deployment=settings.azure_openai_model,
        temperature=0.1,
    )


def verify_evidence(parsed_constraints: dict, evidence_summary: dict) -> VerifierOutput:
    """
    Verify collected evidence matches constraints.
    
    Args:
        parsed_constraints: Parsed constraint object
        evidence_summary: Summary of collected evidence
        
    Returns:
        VerifierOutput with pass/fail status
    """
    llm = get_llm_client()
    
    # Format constraints as JSON string
    constraints_str = json.dumps(parsed_constraints, indent=2)
    evidence_str = json.dumps(evidence_summary, indent=2)
    
    prompt = VERIFIER_PROMPT.replace("{parsed_constraints}", constraints_str).replace("{evidence_summary}", evidence_str)
    
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
        
        result_dict = json.loads(response_text)
        return VerifierOutput(**result_dict)
        
    except Exception as e:
        print(f"Error in verification: {str(e)}")
        # Default to fail on error
        return VerifierOutput(
            is_passed=False,
            fail_reasons=[f"Verification error: {str(e)}"],
            constraint_violations={},
            retry_query_suggestions=[],
            coverage_score=0
        )


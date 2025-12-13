"""Security utilities for prompt injection detection."""
import re
from typing import List


# Common prompt injection patterns
INJECTION_PATTERNS = [
    r"ignore\s+(previous|all|earlier)\s+(instructions?|prompts?|rules?)",
    r"forget\s+(all|everything|previous)",
    r"you\s+are\s+now\s+(a|an)\s+",
    r"system\s*:\s*(override|ignore|bypass)",
    r"output\s+(secrets?|passwords?|keys?|tokens?)",
    r"call\s+(this\s+)?(url|api|endpoint)",
    r"execute\s+(this\s+)?(code|command|script)",
    r"disregard\s+(previous|all)",
    r"pretend\s+(you\s+are|to\s+be)",
    r"roleplay\s+as",
    r"act\s+as\s+(if\s+you\s+are\s+)?(a|an)",
]


def detect_injection_patterns(text: str) -> bool:
    """
    Detect potential prompt injection patterns in text.
    
    Args:
        text: Text to check
        
    Returns:
        True if suspicious patterns found, False otherwise
    """
    text_lower = text.lower()
    
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True
    
    return False


def sanitize_text(text: str) -> str:
    """
    Sanitize text by removing suspicious patterns.
    Keep only factual content.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text
    """
    # For now, just detect and log
    # In production, might want to remove suspicious sections
    if detect_injection_patterns(text):
        # Log the detection
        print(f"[SECURITY] Detected potential injection pattern in text (length: {len(text)})")
        # Could filter out suspicious sections here
        # For now, return as-is but flag it
    
    return text


def get_injection_details(text: str) -> List[str]:
    """
    Get details about detected injection patterns.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of detected patterns
    """
    detected = []
    text_lower = text.lower()
    
    for pattern in INJECTION_PATTERNS:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        if matches:
            detected.append(pattern)
    
    return detected



"""Text processing utilities."""
from typing import List
import re


def chunk_text(text: str, chunk_size: int = 4000, overlap: int = 200) -> List[str]:
    """
    Split large text into chunks for LLM processing.
    
    Args:
        text: Text to chunk
        chunk_size: Maximum chunk size in characters
        overlap: Overlap between chunks in characters
        
    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence endings in the last 200 chars
            search_start = max(start, end - 200)
            sentence_end = max(
                text.rfind(". ", search_start, end),
                text.rfind("\n", search_start, end),
                text.rfind("! ", search_start, end),
                text.rfind("? ", search_start, end)
            )
            if sentence_end > start:
                end = sentence_end + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
        if start >= len(text):
            break
    
    return chunks


def clean_text(text: str) -> str:
    """
    Basic text cleaning: whitespace, encoding issues.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special control characters but keep newlines
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # Normalize newlines
    text = re.sub(r'\r\n|\r', '\n', text)
    
    # Trim
    text = text.strip()
    
    return text


def normalize_topic(topic: str) -> str:
    """
    Normalize topic name: lowercase, strip, remove noise.
    
    Args:
        topic: Topic name to normalize
        
    Returns:
        Normalized topic name
    """
    if not topic:
        return ""
    
    # Lowercase
    normalized = topic.lower()
    
    # Strip whitespace
    normalized = normalized.strip()
    
    # Remove common prefixes/suffixes
    normalized = re.sub(r'^(the|a|an)\s+', '', normalized)
    
    # Remove trailing punctuation
    normalized = re.sub(r'[^\w\s]+$', '', normalized)
    
    return normalized


def compute_embedding_similarity(text1: str, text2: str) -> float:
    """
    Compute similarity between two texts (placeholder for embedding-based similarity).
    
    For now, uses simple word overlap. Could be enhanced with embeddings.
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score 0-1
    """
    # Simple word overlap-based similarity
    words1 = set(normalize_topic(text1).split())
    words2 = set(normalize_topic(text2).split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    if not union:
        return 0.0
    
    return len(intersection) / len(union)



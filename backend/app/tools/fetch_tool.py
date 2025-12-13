"""Web page fetching and content extraction tool."""
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any
import hashlib
from urllib.parse import urlparse


def fetch_web_page(url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Fetch web page content and extract text.
    
    Args:
        url: URL to fetch
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary with:
        - url: Original URL
        - title: Page title
        - snippet: First 500 chars of text
        - raw_text: Full extracted text
        - status: "success", "blocked", "timeout", or "error"
        - content_hash: SHA-256 hash of content for deduplication
    """
    result = {
        "url": url,
        "title": "",
        "snippet": "",
        "raw_text": "",
        "status": "error",
        "content_hash": None
    }
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        
        if response.status_code == 403 or response.status_code == 401:
            result["status"] = "blocked"
            result["snippet"] = f"Access blocked (HTTP {response.status_code})"
            return result
            
        if response.status_code != 200:
            result["status"] = "error"
            result["snippet"] = f"HTTP {response.status_code}"
            return result
        
        # Parse HTML
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract title
        title_tag = soup.find("title")
        result["title"] = title_tag.get_text(strip=True) if title_tag else ""
        
        # Remove script and style elements
        for script in soup(["script", "style", "meta", "link"]):
            script.decompose()
        
        # Extract text
        text = soup.get_text(separator=" ", strip=True)
        # Clean up whitespace
        text = " ".join(text.split())
        
        result["raw_text"] = text
        result["snippet"] = text[:500] if len(text) > 500 else text
        result["status"] = "success"
        
        # Generate content hash
        result["content_hash"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
        
    except requests.exceptions.Timeout:
        result["status"] = "timeout"
        result["snippet"] = "Request timeout"
    except requests.exceptions.ConnectionError:
        result["status"] = "error"
        result["snippet"] = "Connection error"
    except Exception as e:
        result["status"] = "error"
        result["snippet"] = f"Error: {str(e)}"
    
    return result


def extract_company_from_url(url: str) -> str:
    """
    Extract company name from URL if possible.
    
    Args:
        url: Job posting URL
        
    Returns:
        Company name or empty string
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Common patterns
        if "greenhouse.io" in domain:
            # Greenhouse URLs often have company name in path
            parts = parsed.path.strip("/").split("/")
            if parts:
                return parts[0].replace("-", " ").title()
        elif "lever.co" in domain:
            parts = parsed.path.strip("/").split("/")
            if parts:
                return parts[0].replace("-", " ").title()
        elif "jobs" in domain:
            # Try to extract from subdomain
            subdomain = domain.split(".")[0]
            if subdomain != "www" and subdomain != "jobs":
                return subdomain.replace("-", " ").title()
                
    except Exception:
        pass
    
    return ""



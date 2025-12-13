"""Web search tool using Tavily."""
from langchain_tavily import TavilySearch
from app.core.config import settings


def create_search_tool() -> TavilySearch:
    """
    Create Tavily web search tool.
    
    Returns:
        TavilySearch tool instance
    """
    if not settings.tavily_api_key or settings.tavily_api_key == "your_tavily_key_here":
        raise ValueError(
            "TAVILY_API_KEY not set in .env file. "
            "Please set TAVILY_API_KEY=your_key in backend/.env"
        )
    
    tool = TavilySearch(
        tavily_api_key=settings.tavily_api_key,
        max_results=10,
        search_depth="advanced"  # Use advanced search for better results
    )
    
    return tool


# For direct use (non-LangChain)
def search_web(query: str, max_results: int = 10) -> list:
    """
    Search the web using Tavily API directly.
    
    Args:
        query: Search query string
        max_results: Maximum number of results
        
    Returns:
        List of search results with url, title, content, etc.
    """
    import tavily
    
    if not settings.tavily_api_key or settings.tavily_api_key == "your_tavily_key_here":
        raise ValueError("TAVILY_API_KEY not set in .env file")
    
    client = tavily.TavilyClient(api_key=settings.tavily_api_key)
    
    response = client.search(
        query=query,
        max_results=max_results,
        search_depth="advanced"
    )
    
    return response.get("results", [])


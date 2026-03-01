import os
from tavily import TavilyClient

def get_tavily_client() -> TavilyClient:
    api_key = os.getenv("TAVILY_API_KEY", "")
    if not api_key:
        raise RuntimeError("Missing TAVILY_API_KEY")
    return TavilyClient(api_key=api_key)
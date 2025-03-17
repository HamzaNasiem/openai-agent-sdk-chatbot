from agents.tool import function_tool
from tavily import TavilyClient
import wikipediaapi
import chainlit as cl
import os

# Load Tavily API key
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Initialize Tavily client
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
wiki_wiki = wikipediaapi.Wikipedia(
    language='en',
    user_agent='MyAIAgent/1.0 (contact: ziaee.pk@gmail.com)'  # User agent specify karna zaroori hai
)

# -----------------------------------------
# Web search Tool
# -----------------------------------------

@function_tool
@cl.step(type="web search tool")
def web_search(query: str) -> str:
    """
    Web search function using Tavily API.

    Args:
        query (str): Search query.

    Returns:
        str: Search results or "No results found."
    """
    results = tavily_client.search(query)
    return results if results else "No results found."

# -----------------------------------------
# Wiki search Tool
# -----------------------------------------

@function_tool
@cl.step(type="wikipedia search tool")
def wikipedia_search(query: str) -> str:
    """
    Perform a Wikipedia search for a given query.

    Args:
        query (str): Search query.

    Returns:
        str: Summary or "No results found."
    """
    page = wiki_wiki.page(query)

    if not page.exists():
        return "No results found on Wikipedia."

    # Return up to 1000 characters of the summary
    return page.summary[:1000] + ("..." if len(page.summary) > 1000 else "")

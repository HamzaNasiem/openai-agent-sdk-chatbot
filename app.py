import os
from typing import List, cast
from dotenv import load_dotenv
from agents import AsyncOpenAI, OpenAIChatCompletionsModel, Agent, Runner
from agents.run import RunConfig
from agents.tool import function_tool
import chainlit as cl
from tavily import TavilyClient

# -----------------------------------------
# Load environment variables from .env file
# -----------------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY  = os.getenv("TAVILY_API_KEY ")


# Initialize Tavily API client for web search
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

# -----------------------------------------
# Web Search Tool Definition
# -----------------------------------------
@function_tool
@cl.step(type="web search tool")
def web_search(query: str) -> str:
    """
    Perform web search using Tavily API.

    Args:
        query (str): Search query.

    Returns:
        str: Search results or "No results found."
    """
    results = tavily_client.search(query)  # Perform search
    if not results:
        return "No results found."  # No results case
    return results  # Return search results

# -----------------------------------------
# Chat Start Handler
# Initialize Agent
# -----------------------------------------
@cl.on_chat_start
async def start():
    # Initialize OpenAI API client
    external_client = AsyncOpenAI(
        api_key=GEMINI_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    # Set OpenAI model configuration
    model = OpenAIChatCompletionsModel(
        model="gemini-2.0-flash",
        openai_client=external_client
    )

    # Runner configuration
    config = RunConfig(
        model=model,
        model_provider=external_client,
        tracing_disabled=True  # Disable tracing/logging
    )

    # Initialize user session variables
    cl.user_session.set("chat_history", [])  # Empty chat history
    cl.user_session.set("config", config)  # Runner configuration

    # Define chatbot agent
    agent: Agent = Agent(
        name="Bob",
        instructions=(
            "You are a helpful assistant tasked with web searching "
            "or providing information. Use 'web_search' if external info is needed."
        ),
        tools=[web_search],  # Available tools
        model=model
    )

    # Store agent in user session
    cl.user_session.set("agent", agent)

    # Welcome message to user (optional)
    await cl.Message(content="Welcome to My Agentic World! How can I help you?").send()

# -----------------------------------------
# Handle Incoming User Messages
# -----------------------------------------
@cl.on_message
async def handle_message(message: cl.Message):
    """
    Handle user messages and generate chatbot responses.

    Args:
        message (cl.Message): Incoming user message.
    """
    # Inform user that bot is processing the query
    msg = cl.Message(content="Thinking...")
    await msg.send()

    # Retrieve agent and config from user session
    agent: Agent = cast(Agent, cl.user_session.get("agent"))
    config: RunConfig = cast(RunConfig, cl.user_session.get("config"))
    
    # Get chat history or initialize if not present
    history = cl.user_session.get("chat_history") or []

    # Append user message to history
    history.append({
        "role": "user",
        "content": message.content
    })

    # Run agent with current chat history
    result = Runner.run_streamed(
        agent,
        input=history,
        run_config=config
    )

    # Stream assistant's response token by token
    async for event in result.stream_events():
        if event.type == "raw_response_event" and hasattr(event.data, 'delta'):
            token = event.data.delta  # Get token from event
            await msg.stream_token(token)  # Stream token to user

    # Get final response from agent
    response_content = result.final_output

    # Update the chatbot message with the final response
    msg.content = response_content
    await msg.update()

    # Append assistant's response to chat history
    history.append({
        "role": "assistant",
        "content": msg.content
    })

    # Update user session with updated history
    cl.user_session.set("chat_history", history)

    # Debugging: Print user and assistant messages to console
    print(f"User: {message.content}")
    print(f"Assistant: {msg.content}")

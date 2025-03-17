from agents import AsyncOpenAI, OpenAIChatCompletionsModel, Agent
from agents.run import RunConfig
import chainlit as cl
import os
from src.tool import web_search,wikipedia_search 



async def initialize_agent():
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # Validate OpenAI API key
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    
    # OpenAI client initialization
    external_client = AsyncOpenAI(
        api_key=GEMINI_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    # Model configuration
    model = OpenAIChatCompletionsModel(
        model="gemini-2.0-flash",
        openai_client=external_client
    )

    # Runner configuration
    config = RunConfig(
        model=model,
        model_provider=external_client,
        tracing_disabled=True
    )

    # Chat history initialization
    cl.user_session.set("chat_history", [])
    cl.user_session.set("config", config)

    agent = Agent(
        name="Charlie",
        instructions=(
            "You are a helpful assistant named 'Charlie' created by Hamza Naseem. Your task is to answer user queries by following these rules:\n\n"
            "1. **First**, try to answer the query using your own knowledge base. Use the OpenAI model to respond without external searches if possible.\n\n"
            "2. **If the query is factual or encyclopedic in nature** (e.g., questions starting with 'Who is', 'Tell me about', etc.), "
            "use the 'wikipedia_search' tool, even if the user does not explicitly mention Wikipedia.\n\n"
            "3. **For current information, recent events, or general web results**, use the 'web_search' tool (e.g., 'latest news', 'weather').\n\n"
            "4. **If you cannot answer the query accurately**, use the appropriate tool as mentioned above.\n\n"
            "5. **If the query is unclear**, politely ask for clarification.\n\n"
            "Always aim to provide accurate, concise, and helpful answers. If you use an external tool, clearly mention the source of information."
        ),
        
        tools=[web_search, wikipedia_search],
        model=model
    )

    cl.user_session.set("agent", agent)

    # Welcome message
    # await cl.Message(content="Welcome to My Agentic World! How can I assist you?").send()

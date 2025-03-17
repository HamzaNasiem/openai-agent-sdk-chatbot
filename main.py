import os
from dotenv import load_dotenv
import chainlit as cl
from src.agents_config import initialize_agent
from src.handlers import handle_message

# Load environment variables
load_dotenv()

# Chat start event handler
@cl.on_chat_start
async def start():
    await initialize_agent()  # Initialize OpenAI and Agent

# Message handler for incoming user messages
@cl.on_message
async def on_message(message: cl.Message):
    await handle_message(message)

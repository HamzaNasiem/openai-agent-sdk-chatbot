import chainlit as cl

async def send_message(content: str):
    """Send a message via Chainlit."""
    await cl.Message(content=content).send()

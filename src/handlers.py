from agents import Agent, RunConfig, Runner
import chainlit as cl
from typing import cast

async def handle_message(message: cl.Message):
    """
    Handle user messages and process chatbot response.

    Args:
        message (cl.Message): Incoming user message.
    """
    msg = cl.Message(content="Thinking...")
    await msg.send()

    agent = cast(Agent, cl.user_session.get("agent"))
    config = cast(RunConfig, cl.user_session.get("config"))
    history = cl.user_session.get("chat_history") or []

    # Update chat history with user's message
    history.append({
        "role": "user",
        "content": message.content
    })

    # Generate assistant's response
    result = Runner.run_streamed(agent, input=history, run_config=config)

    # Stream assistant's response
    async for event in result.stream_events():
        if event.type == "raw_response_event" and hasattr(event.data, "delta"):
            token = event.data.delta
            await msg.stream_token(token)

    # Finalize response and update history
    response_content = result.final_output
    msg.content = response_content
    await msg.update()

    history.append({
        "role": "assistant",
        "content": msg.content
    })

    cl.user_session.set("chat_history", history)

    # Debug output
    print(f"User: {message.content}")
    print(f"Assistant: {msg.content}")

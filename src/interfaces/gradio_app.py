import gradio as gr
import asyncio
import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.services.openai_service import OpenAIService, MessageHistory, CompletionConfig
from dotenv import load_dotenv
from typing import AsyncGenerator, Union

# Load environment variables
load_dotenv()

# Initialize OpenAI service
openai_service = OpenAIService()

# Store active conversations
conversations = {}

async def chat(message: str, history):
    """Chat function that integrates with OpenAI service."""
    try:
        # Get or create conversation history
        session_id = None
        for sess_id, conv in conversations.items():
            if len(conv.messages) >= 2 and conv.messages[1].content == history[0][0]:
                session_id = sess_id
                message_history = conv
                break
        
        if not session_id:
            message_history = MessageHistory()
            message_history.add_message(
                role="system",
                content="You are a helpful AI assistant. Be concise, friendly, and provide accurate information."
            )
            conversations[message_history.session_id] = message_history

        # Add user message to history
        message_history.add_message(role="user", content=message)
        
        # Get response from OpenAI
        config = CompletionConfig(stream=True)
        response = await openai_service.completion(message_history, config=config)
        
        if isinstance(response, AsyncGenerator):
            chunks = []
            async for chunk in response:
                chunks.append(chunk)
                yield ''.join(chunks)
            
            # Add complete response to history
            complete_response = ''.join(chunks)
            if complete_response:
                message_history.add_message(role="assistant", content=complete_response)
        else:
            message_history.add_message(role="assistant", content=str(response))
            yield str(response)

    except Exception as e:
        yield f"Error: {str(e)}"

# Create and launch the Gradio interface
demo = gr.ChatInterface(
    fn=chat,
    title="🤖 AI Assistant",
    description="Chat with an AI assistant powered by OpenAI",
    examples=["Hello, how are you?", "What can you help me with?"],
)

if __name__ == "__main__":
    demo.launch()
from flask import Flask, request, jsonify, Response, stream_with_context
from clasess.OpenAIService import OpenAIService, MessageHistory, CompletionConfig
import asyncio
from dotenv import load_dotenv
from typing import AsyncGenerator
from asgiref.sync import async_to_sync
import json

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize OpenAI service
openai_service = OpenAIService()

# Store active conversations
conversations = {}

@app.route('/chat/stream', methods=['POST'])
def chat_stream():
    try:
        data = request.get_json()
        message = data.get('message')
        session_id = data.get('session_id')

        if not message:
            return jsonify({'error': 'Message is required'}), 400

        # Get or create conversation history
        if session_id and session_id in conversations:
            message_history = conversations[session_id]
        else:
            message_history = MessageHistory()
            if not message_history.messages:  # If new conversation
                message_history.add_message(
                    role="system",
                    content="You are a helpful AI assistant. Be concise, friendly, and provide accurate information."
                )
            conversations[message_history.session_id] = message_history

        # Add user message to history
        message_history.add_message(role="user", content=message)

        async def get_stream():
            config = CompletionConfig(stream=True)
            response = await openai_service.completion(message_history, config=config)
            
            if isinstance(response, AsyncGenerator):
                chunks = []
                async for chunk in response:
                    if chunk:
                        chunks.append(chunk)
                        yield f"data: {json.dumps({'chunk': chunk, 'session_id': message_history.session_id})}\n\n"
                
                # Add complete response to history
                complete_response = ''.join(chunks)
                if complete_response:
                    message_history.add_message(role="assistant", content=complete_response)

        def generate():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                async_gen = get_stream()
                while True:
                    try:
                        # Run the coroutine in the event loop
                        chunk = loop.run_until_complete(async_gen.__anext__())
                        yield chunk
                    except StopAsyncIteration:
                        break
            finally:
                loop.close()

        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message')
        session_id = data.get('session_id')

        if not message:
            return jsonify({'error': 'Message is required'}), 400

        # Get or create conversation history
        if session_id and session_id in conversations:
            message_history = conversations[session_id]
        else:
            message_history = MessageHistory()
            if not message_history.messages:  # If new conversation
                message_history.add_message(
                    role="system",
                    content="You are a helpful AI assistant. Be concise, friendly, and provide accurate information."
                )
            conversations[message_history.session_id] = message_history

        # Add user message to history
        message_history.add_message(role="user", content=message)
        
        # Get response from OpenAI using async_to_sync
        async def get_response():
            response = await openai_service.completion(message_history)
            
            # Handle streaming response if it's an async generator
            if isinstance(response, AsyncGenerator):
                full_response = []
                async for chunk in response:
                    full_response.append(chunk)
                return ''.join(full_response)
            return response

        response = async_to_sync(get_response)()
        
        # Add assistant response to history
        message_history.add_message(role="assistant", content=response)
        
        return jsonify({
            'response': response,
            'session_id': message_history.session_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/conversations/<session_id>', methods=['GET'])
def get_conversation(session_id):
    if session_id not in conversations:
        return jsonify({'error': 'Conversation not found'}), 404
    
    message_history = conversations[session_id]
    return jsonify({
        'session_id': session_id,
        'messages': [
            {'role': msg.role.value, 'content': msg.content}
            for msg in message_history.messages
        ]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True) 
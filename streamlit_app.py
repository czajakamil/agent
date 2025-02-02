import streamlit as st
import requests
import json
from urllib.parse import urljoin
import os
from requests.exceptions import RequestException

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
CHAT_ENDPOINT = urljoin(API_BASE_URL, '/chat/stream')

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "error" not in st.session_state:
    st.session_state.error = None

st.title("🤖 AI Chatbot")

# Clear chat button
if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []
    st.session_state.session_id = None
    st.session_state.error = None
    st.rerun()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What's on your mind?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Prepare the request
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    data = {
        "message": prompt,
        "session_id": st.session_state.session_id
    }
    
    # Create a placeholder for the assistant's response
    with st.chat_message("assistant"):
        try:
            with requests.post(CHAT_ENDPOINT, headers=headers, json=data, stream=True) as response:
                response.raise_for_status()
                
                def event_stream():
                    for line in response.iter_lines(decode_unicode=True):
                        if line.startswith('data: '):
                            try:
                                chunk_data = json.loads(line[6:])  # Skip 'data: ' prefix
                                st.session_state.session_id = chunk_data['session_id']
                                yield chunk_data['chunk']
                            except json.JSONDecodeError:
                                continue
                
                # Use Streamlit's write_stream to handle the streaming response
                full_response = st.write_stream(event_stream())
                
                # Add assistant response to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response
                })
                
        except RequestException as e:
            error_message = f"Connection error: {str(e)}"
            st.error(error_message)
            st.session_state.error = error_message
        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"
            st.error(error_message)
            st.session_state.error = error_message

# Display any persistent error in the sidebar
if st.session_state.error:
    st.sidebar.error(st.session_state.error)
    if st.sidebar.button("Clear Error"):
        st.session_state.error = None
        st.rerun() 
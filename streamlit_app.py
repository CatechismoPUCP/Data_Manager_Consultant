import streamlit as st
import os
import google.generativeai as genai
from datetime import datetime
import time
import re

# Page config
st.set_page_config(
    page_title="Data Governance Assistant",    
    page_icon="🎯",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    /* Gradient animated title */
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .title-container {
        background: linear-gradient(-45deg, #007bff, #28a745, #00bcd4, #6772e5);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .main-title {
        color: white;
        font-size: 3rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        margin: 0;
    }
    
    .subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
        margin-top: 0.5rem;
    }
    
    /* Chat messages */
    .user-message {
        background-color: #f8f9fa;
        border-left: 4px solid #007bff;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .assistant-message {
        background-color: #ffffff;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Notion-like typing animation */
    @keyframes typing {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .typing {
        animation: typing 0.5s ease-in-out;
    }
    
    /* Input area */
    .stTextArea textarea {
        border: 2px solid #e1e4e8;
        border-radius: 10px;
        font-size: 1rem;
        padding: 10px;
    }
    
    .stTextArea textarea:focus {
        border-color: #007bff;
        box-shadow: 0 0 0 2px rgba(0,123,255,.25);
    }
    
    /* Buttons */
    .stButton button {
        border-radius: 20px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Title section
st.markdown("""
    <div class="title-container">
        <h1 class="main-title">🎯 Data Governance Assistant</h1>
        <p class="subtitle">Your intelligent companion for data governance and unification</p>
    </div>
""", unsafe_allow_html=True)

# Initialize Gemini
def initialize_gemini():
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("Please set GEMINI_API_KEY in your Streamlit secrets")
        st.stop()
    
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    
    try:
        with open("system_prompt.txt", "r") as f:
            system_prompt = f.read()
    except FileNotFoundError:
        st.error("system_prompt.txt file not found")
        st.stop()
    
    return genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
        system_instruction=system_prompt
    )

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session" not in st.session_state:
    model = initialize_gemini()
    st.session_state.chat_session = model.start_chat(history=[])

# Extract answer from response
def extract_answer(response_text):
    try:
        answer_match = re.search(r'<answer>(.*?)</answer>', response_text, re.DOTALL)
        if answer_match:
            return answer_match.group(1).strip()
        return response_text  # Return full text if no answer tags found
    except Exception:
        return response_text

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"""
            <div class="user-message">
                <strong>You:</strong><br>
                {message["content"]}
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="assistant-message">
                <strong>Assistant:</strong><br>
                {extract_answer(message["content"])}
            </div>
        """, unsafe_allow_html=True)

# Chat input
with st.container():
    user_input = st.text_area("Ask your question:", height=100, key="input")
    col1, col2 = st.columns([1, 5])
    
    with col1:
        submit_button = st.button("Send", use_container_width=True)
    with col2:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            model = initialize_gemini()
            st.session_state.chat_session = model.start_chat(history=[])
            st.rerun()

# Handle chat interaction
if submit_button and user_input:
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Create placeholder for streaming response
    response_placeholder = st.empty()
    
    try:
        # Get response
        response = st.session_state.chat_session.send_message(user_input)
        
        # Simulate Notion-like typing effect
        full_response = response.text
        words = extract_answer(full_response).split()
        current_response = ""
        
        for i, word in enumerate(words):
            current_response += word + " "
            response_placeholder.markdown(f"""
                <div class="assistant-message typing">
                    <strong>Assistant:</strong><br>
                    {current_response}
                </div>
            """, unsafe_allow_html=True)
            time.sleep(0.05)  # Adjust speed of typing effect
        
        # Add to message history
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response
        })
        
        st.rerun()
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        

# Add some spacing at the bottom
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    This AI assistant specializes in data governance and data unification, drawing knowledge from:
    - "Aligning Business and Data" by Ron Itelman and Juan Cruz Viotti
    - "Data Governance: The Definitive Guide" by Evren Eryurek et al.
""")

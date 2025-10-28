import streamlit as st
import requests
import os
from typing import Optional

# --- Configuration ---
# CRITICAL: Use the service name 'backend' when running in Docker Compose
API_BASE_URL = "http://backend:8000/api/chat"
USER_ID = "demo_user" 

# Since we are removing the selector, we define the source as a constant
GEMINI_LLM_SOURCE = "Gemini API (Cloud)"

# --- UI Setup ---
st.set_page_config(page_title="🧠 PyCoach: Adaptive Python Tutor", layout="wide")
st.title("🧠 PyCoach: The Adaptive Python Tutor")
st.markdown("A portfolio project demonstrating **RAG**, **Adaptive Prompting**, and **Level-Based Tutoring** using the **Gemini API**.")

# --- Session State Initialization ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'profile' not in st.session_state:
    # Initialize with a default level
    st.session_state.profile = {"current_level": "Beginner"}
if 'user_key_input' not in st.session_state: 
    st.session_state.user_key_input = ""

# ----------------------------------------


# --- CORE API CALL LOGIC ---
def call_backend_api(prompt: str, key: Optional[str], current_level: str):
    """Calls the FastAPI backend with the message, key, and current adaptive level."""

    # The key is passed only if the user provides it in the sidebar. 
    # If not provided, the backend attempts to use the GEMINI_API_KEY environment variable.
    api_key_to_use = key if key else None
    
    data = {
        "user_id": USER_ID,
        "message": prompt,
        "api_key": api_key_to_use, 
        "llm_source": GEMINI_LLM_SOURCE, # Source is now fixed
        "current_level": current_level
    }

    try:
        response = requests.post(
            API_BASE_URL,
            json=data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status() 

        response_data = response.json()
        
        # Update profile level based on backend response
        st.session_state.profile['current_level'] = response_data.get("current_level", "N/A")
        
        return response_data.get("response", "Error: No response from tutor.")

    except requests.exceptions.HTTPError as e:
        error_detail = e.response.json().get("detail", "Unknown API Error.")
        
        # Update the error message to reflect Gemini as the only source
        if "429" in error_detail or "quota" in error_detail.lower():
            return f"❌ **QUOTA EXCEEDED (429)**: The Gemini API limit was reached. Please check your usage."
        
        if "API Key is missing" in error_detail:
            return "❌ **Authentication Error**: Gemini API Key is missing. Please enter your personal key in the sidebar."
            
        return f"❌ Backend HTTP Error ({e.response.status_code}): {error_detail}"
        
    except requests.exceptions.ConnectionError:
        # Update connection error message
        return "❌ **Connection Error**: The FastAPI backend is not running at `http://backend:8000`. Please ensure you run `docker compose up --build`."
    except Exception as e:
        return f"❌ An unexpected error occurred: {e}"


# --- UI SIDEBAR: Control Panel & Dashboard ---
with st.sidebar:
    st.header("⚙️ Gemini API Authentication")
    
    # 1. Key Input (Simplified to only Gemini key)
    st.session_state.user_key_input = st.text_input(
        "Enter your personal Gemini API Key:", 
        type="password",
        value=st.session_state.user_key_input 
    )
    custom_key = st.session_state.user_key_input 

    if custom_key:
        st.success(f"Key Loaded for {GEMINI_LLM_SOURCE}.")
    else:
        st.warning(f"Using environment variable key (if available). Enter a key to override.")
    
    st.markdown("---")
    st.header("⚙️ Adaptive Level Control")
    
    new_level = st.selectbox(
        "Manually Set Tutor Difficulty:",
        options=["Beginner", "Intermediate", "Expert"],
        index=["Beginner", "Intermediate", "Expert"].index(st.session_state.profile.get('current_level', 'Beginner'))
    )
    
    # Update the session profile if the selection changes
    st.session_state.profile['current_level'] = new_level
    st.info(f"Tutor difficulty set to **{new_level}**.")

    st.markdown("---")
    st.header("📊 Learner Status Dashboard")
    
    current_level = st.session_state.profile.get('current_level', 'Beginner')
    
    st.subheader("Current Adaptive Pace")
    st.metric(label="Tutor Difficulty Level", value=current_level)

    # --- Topic Coverage Placeholder ---
    st.markdown("---")
    st.markdown("### 📚 Knowledge Base Focus")
    st.caption("Content: Python Fundamentals, Control Flow, Data Structures (Lists/Dicts/Tuples).")
    
    # --- Skill Hints Placeholder (Based on Current Level) ---
    st.markdown("---")
    st.markdown("### 💡 Next Skill Hint")
    if current_level == 'Beginner':
        st.warning("Try solving a problem using a `for` loop or ask 'How do lists work?'")
    elif current_level == 'Intermediate':
        st.warning("Focus on **Object-Oriented Programming (OOP)** or **Error Handling (`try/except`)**.")
    else:
        st.warning("Challenge yourself with **Concurrency (Asyncio)** or complex algorithm implementation.")

    st.markdown("---")
    if st.button("🔄 Reset Session"):
        st.session_state.history = []
        st.session_state.profile = {"current_level": "Beginner"} 
        st.session_state.user_key_input = "" 
        st.rerun()


# --- MAIN CHAT INTERFACE ---

for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a Python question (e.g., 'What is a list comprehension?')"):
    
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response from backend
    current_level = st.session_state.profile.get('current_level', 'Beginner')
    
    with st.spinner(f"PyCoach is using {GEMINI_LLM_SOURCE} to think..."):
        # The llm_source parameter is implicitly passed by the fixed value in the function definition
        tutor_response = call_backend_api(prompt, custom_key, current_level)

    # Display tutor response
    st.session_state.history.append({"role": "assistant", "content": tutor_response})
    with st.chat_message("assistant"):
        st.markdown(tutor_response)

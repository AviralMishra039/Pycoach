import streamlit as st
import requests
import os
import pandas as pd
from typing import Optional

# --- Configuration ---
API_BASE_URL = "http://127.0.0.1:8000/api/chat"
USER_ID = "demo_user" 

# --- UI Setup ---
st.set_page_config(page_title=" PyCoach: Adaptive Python Tutor", layout="wide")
st.title(" PyCoach: The Adaptive Python Tutor")
st.markdown("A portfolio project demonstrating **RAG**, **Adaptive Prompting**, and **Level-Based Tutoring**.")

# --- Session State Initialization ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'profile' not in st.session_state:
   
    st.session_state.profile = {"current_level": "Beginner"}
if 'llm_source' not in st.session_state:
    st.session_state.llm_source = "Gemini API (Personal Key)"

if 'user_key_input' not in st.session_state: 
    st.session_state.user_key_input = ""

# ----------------------------------------


# --- CORE API CALL LOGIC ---
def call_backend_api(prompt: str, key: Optional[str], llm_source: str, current_level: str):
    """Calls the FastAPI backend with the message, key, LLM choice, and current adaptive level."""

    # 1. Determine which key to pass
    api_key_to_use = None
    if llm_source == "Gemini API (Personal Key)" and key:
        api_key_to_use = key
    
    data = {
        "user_id": USER_ID,
        "message": prompt,
        "api_key": api_key_to_use, 
        "llm_source": llm_source,
        #  PASSING THE CURRENT LEVEL FOR DB MANAGER 
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
        
       
        st.session_state.profile['current_level'] = response_data.get("current_level", "N/A")
        
        return response_data.get("response", "Error: No response from tutor.")

    except requests.exceptions.HTTPError as e:
        error_detail = e.response.json().get("detail", "Unknown API Error.")
        if "quota" in error_detail.lower() or "429" in error_detail:
             return f"❌ **QUOTA EXCEEDED (429)**: The API limit was reached. Please switch to the **Local LLM** option or enter your own **Gemini API Key** to continue."
        return f"❌ Backend HTTP Error ({e.response.status_code}): {error_detail}"
    except requests.exceptions.ConnectionError:
        return "❌ **Connection Error**: The FastAPI backend is not running. Please ensure you run `docker compose up -d`."
    except Exception as e:
        return f"❌ An unexpected error occurred: {e}"


# --- UI SIDEBAR: Control Panel & Dashboard  ---
with st.sidebar:
    st.header("⚙️ LLM Source & Authentication")
    
    # 1. Model Source Selector
    llm_source_options = [
        "Gemini API (Personal Key)",
        "Local LLM (Requires Ollama)"
    ]
    st.session_state.llm_source = st.selectbox(
        "Select LLM Source:",
        llm_source_options,
        index=llm_source_options.index(st.session_state.llm_source)
    )

    # 2. Key Input for Hybrid Approach (Using session_state)
    custom_key = None
    if st.session_state.llm_source == "Gemini API (Personal Key)":
        st.session_state.user_key_input = st.text_input(
            "Enter your personal Gemini API Key:", 
            type="password",
            value=st.session_state.user_key_input 
        )
        custom_key = st.session_state.user_key_input 

        if custom_key:
            st.success("Custom Key Loaded.")
        else:
            st.warning("Please enter your key for this mode.")
    
    elif st.session_state.llm_source == "Local LLM (Requires Ollama)":
        st.info("Ensure the Ollama server is running locally and 'llama3' is pulled (via `docker compose up`).")


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
    key_to_pass = custom_key if st.session_state.llm_source == "Gemini API (Personal Key)" else None
    
    with st.spinner(f"PyCoach is using {st.session_state.llm_source} to think..."):
        #  Pass the current level to the backend API call 
        tutor_response = call_backend_api(prompt, key_to_pass, st.session_state.llm_source, current_level)

    # Display tutor response
    st.session_state.history.append({"role": "assistant", "content": tutor_response})
    with st.chat_message("assistant"):
        st.markdown(tutor_response)

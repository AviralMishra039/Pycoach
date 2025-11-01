import streamlit as st
import requests
import os
import pandas as pd
from typing import Optional

# -----------------------------
# CONFIGURATION
# -----------------------------
API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000/api/chat")  
USER_ID = os.getenv("USER_ID", "demo_user")  

st.set_page_config(page_title="PyCoach: Adaptive Python Tutor", layout="wide")

# -----------------------------
# TITLE & DESCRIPTION
# -----------------------------
st.title("🧠 PyCoach: The Adaptive Python Tutor")
st.markdown("""
A portfolio project demonstrating **RAG**, **Adaptive Prompting**, and **Level-Based Tutoring**  
Built using **FastAPI + Streamlit + Gemini API**.
""")

# -----------------------------
# SESSION STATE INITIALIZATION
# -----------------------------
if 'history' not in st.session_state:
    st.session_state.history = []

if 'profile' not in st.session_state:
    st.session_state.profile = {"current_level": "Beginner"}

if 'user_key_input' not in st.session_state:
    st.session_state.user_key_input = ""

# -----------------------------
# BACKEND API CALL FUNCTION
# -----------------------------
def call_backend_api(prompt: str, api_key: Optional[str], current_level: str):
    """Send user query to backend and get tutor response."""
    data = {
        "user_id": USER_ID,
        "message": prompt,
        "api_key": api_key,
        "llm_source": "Gemini API (Personal Key)",
        "current_level": current_level
    }

    try:
        response = requests.post(API_BASE_URL, json=data, timeout=60)
        response.raise_for_status()

        response_data = response.json()
        st.session_state.profile["current_level"] = response_data.get("current_level", current_level)

        return response_data.get("response", "⚠️ Tutor returned no response.")

    except requests.exceptions.ConnectionError:
        return "❌ **Connection Error:** Backend not reachable. Make sure FastAPI server is running."
    except requests.exceptions.Timeout:
        return "⏳ **Timeout:** The backend took too long to respond."
    except requests.exceptions.RequestException as e:
        return f"❌ **HTTP Error:** {str(e)}"
    except Exception as e:
        return f"⚠️ Unexpected error: {str(e)}"


# -----------------------------
# SIDEBAR — SETTINGS & DASHBOARD
# -----------------------------
with st.sidebar:
    st.header("⚙️ Tutor Configuration")

    # API Key
    st.session_state.user_key_input = st.text_input(
        "Enter your Gemini API Key:",
        type="password",
        value=st.session_state.user_key_input
    )

    if st.session_state.user_key_input:
        st.success("✅ API Key Loaded")
    else:
        st.warning("🔑 Please enter your Gemini API Key to begin.")

    st.markdown("---")

    # Adaptive Level Control
    current_level = st.session_state.profile.get("current_level", "Beginner")
    new_level = st.selectbox(
        "Set Tutor Difficulty:",
        ["Beginner", "Intermediate", "Expert"],
        index=["Beginner", "Intermediate", "Expert"].index(current_level)
    )
    st.session_state.profile["current_level"] = new_level
    st.info(f"🎯 Tutor difficulty set to **{new_level}**")

    st.markdown("---")
    st.subheader("📊 Learner Dashboard")
    st.metric(label="Current Tutor Level", value=new_level)

    st.markdown("---")
    st.caption("**Knowledge Areas:** Python Fundamentals, Control Flow, Data Structures")

    st.markdown("### 💡 Skill Suggestion")
    if new_level == "Beginner":
        st.info("Practice `for` loops or ask: *'How do lists work?'*")
    elif new_level == "Intermediate":
        st.info("Focus on **OOP** or **Error Handling** (`try/except`).")
    else:
        st.info("Explore **Asyncio**, **Generators**, or complex algorithms.")

    st.markdown("---")
    if st.button("🔄 Reset Session"):
        st.session_state.clear()
        st.experimental_rerun()


# -----------------------------
# MAIN CHAT INTERFACE
# -----------------------------
for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask your Python question (e.g., 'What is a list comprehension?')"):
    # Append user message
    st.session_state.history.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Get backend response
    api_key = st.session_state.user_key_input
    level = st.session_state.profile.get("current_level", "Beginner")

    with st.spinner("PyCoach is thinking..."):
        tutor_response = call_backend_api(prompt, api_key, level)

    # Display tutor response
    st.session_state.history.append({"role": "assistant", "content": tutor_response})
    with st.chat_message("assistant"):
        st.markdown(tutor_response)

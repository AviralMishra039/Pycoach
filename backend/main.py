# backend/main.py

import os
import time
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationSummaryBufferMemory
from langchain.schema import SystemMessage
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter

from .models import ChatRequest, ChatResponse
from .adaptive_prompt_engine import get_adaptive_prompt
from .db_manager import get_student_profile
from .rag_pipeline import get_retriever, LOCAL_EMBEDDING_MODEL
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

# --- Setup ---
load_dotenv()
app = FastAPI(title="PyCoach Adaptive Tutor API")

# --- Global Initialization ---
try:
    GLOBAL_EMBEDDINGS = HuggingFaceBgeEmbeddings(
        model_name=LOCAL_EMBEDDING_MODEL,
        encode_kwargs={'normalize_embeddings': True}
    )
    GLOBAL_RETRIEVER = get_retriever(GLOBAL_EMBEDDINGS)
    print("✅ SUCCESS: RAG Retriever initialized using local Hugging Face embeddings.")
except Exception as e:
    print(f"❌ FATAL RAG SETUP ERROR: Could not load ChromaDB. Ensure 'chroma_db' exists. Error: {e}")
    GLOBAL_RETRIEVER = None

# Store memory by session (user_id)
SESSION_MEMORIES = {}


# --- Event Hooks ---
@app.on_event("startup")
async def startup_event():
    if GLOBAL_RETRIEVER is None:
        print("⚠️ Warning: RAG retriever failed to initialize. Check 'chroma_db' path or embedding model config.")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = round(time.time() - start_time, 2)
    print(f"{request.method} {request.url.path} completed in {duration}s")
    return response


# --- Helper Functions ---
def get_llm_and_memory(user_id: str, api_key: str | None, llm_source: str):
    """Initializes the LLM and retrieves/creates the memory for the session."""

    if not api_key:
        raise HTTPException(status_code=401, detail="Gemini API Key is missing. Please enter your key in the sidebar.")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
        google_api_key=api_key,
        convert_system_message_to_human=True
    )

    # --- Memory Setup ---
    if user_id not in SESSION_MEMORIES:
        memory = ConversationSummaryBufferMemory(
            llm=llm,
            max_token_limit=8000,
            memory_key="chat_history",
            return_messages=True
        )
        SESSION_MEMORIES[user_id] = memory

        # Initialize tutor persona
        initial_persona_message = (
            "You are PyCoach, a patient, Socratic AI tutor specializing in Python Programming. "
            "Your goal is to guide the learner to the correct answer through questions and hints, "
            "not direct answers. Stay conversational, curious, and adaptive."
        )
        memory.chat_memory.add_message(SystemMessage(content=initial_persona_message))

    return llm, SESSION_MEMORIES[user_id]


# --- Core Chat Endpoint ---
@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if GLOBAL_RETRIEVER is None:
        raise HTTPException(status_code=500, detail="RAG system is not initialized. Run `rag_pipeline.py` first.")

    start_time = time.time()

    # 1. Get LLM, Memory, and Profile
    try:
        llm, memory = get_llm_and_memory(request.user_id, request.api_key, request.llm_source)
    except HTTPException as e:
        raise e

    profile = get_student_profile(request.user_id)
    adaptive_prompt = get_adaptive_prompt(profile)

    # 2. RAG Chain (LCEL)
    context_retrieval_chain = RunnablePassthrough.assign(
        context=itemgetter("question") | GLOBAL_RETRIEVER
    )
    rag_chain = context_retrieval_chain | adaptive_prompt | llm

    # 3. Prepare Inputs and Run Chain
    history = memory.load_memory_variables({})["chat_history"]
    inputs = {
        "question": request.message,
        "chat_history": history
    }

    try:
        result = rag_chain.invoke(inputs)
        tutor_response = result.content
    except Exception as e:
        error_msg = f"LLM Generation Failed. Error: {e}"
        if "429" in str(e) or "quota" in str(e).lower():
            error_msg = f"QUOTA EXCEEDED (429): Gemini API usage limit hit. Please wait or use another key."
        raise HTTPException(status_code=503, detail=error_msg)

    # 4. Save conversation to memory
    memory.save_context({"input": request.message}, {"output": tutor_response})

    # 5. Return final structured response
    return ChatResponse(
        response=tutor_response,
        current_level=profile.current_level,
        source_documents=[]
    )


# --- Start Server ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

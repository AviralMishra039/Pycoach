# backend/main.py

import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms import Ollama # For Local LLM (Llama 3)
from langchain_community.chat_models import ChatOllama
from langchain.memory import ConversationSummaryBufferMemory
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain.schema import SystemMessage
from operator import itemgetter
import time

from .models import ChatRequest, ChatResponse, StudentProfile
from .adaptive_prompt_engine import get_adaptive_prompt
from .db_manager import get_student_profile, save_student_profile


from langchain_community.embeddings import HuggingFaceBgeEmbeddings 
from .rag_pipeline import get_retriever, LOCAL_EMBEDDING_MODEL 

# --- Setup ---
load_dotenv()
app = FastAPI(title="PyCoach Adaptive Tutor API")

# --- Global Initialization ---
# The embedding function is needed later to load the ChromaDB retriever
try:
    GLOBAL_EMBEDDINGS = HuggingFaceBgeEmbeddings(
        model_name=LOCAL_EMBEDDING_MODEL,
        encode_kwargs={'normalize_embeddings': True}
    )
    # Pass the corrected embedding function to the retriever loader
    GLOBAL_RETRIEVER = get_retriever(GLOBAL_EMBEDDINGS)
    print("SUCCESS: RAG Retriever initialized using local Hugging Face embeddings.")
    
except Exception as e:
    print(f"FATAL RAG SETUP ERROR: Could not load ChromaDB. Ensure 'chroma_db' exists. Error: {e}")
    GLOBAL_RETRIEVER = None
# Store memory by session (user_id).
SESSION_MEMORIES = {}
# -----------------------------


def get_llm_and_memory(user_id: str, api_key: str | None, llm_source: str):
    """Initializes the LLM and retrieves/creates the memory for the session."""

    llm = None
    key_to_use = api_key 

    # --- LLM Selection Logic ---
    if llm_source.startswith("Gemini API"):
        # Gemini Model (Cloud API)
        if not key_to_use:
            raise HTTPException(status_code=401, detail="Gemini API Key is missing. Please enter your personal key in the sidebar.")
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            temperature=0.3, 
            google_api_key=key_to_use,
            convert_system_message_to_human=True
        )
    
    elif llm_source == "Local LLM (Requires Ollama)":
        # Local Llama Model (Zero Cost, User-Hosted)
        try:
            llm = ChatOllama(model="llama3", temperature=0.3)
            # Quick test to verify connectivity to the local server
            llm.invoke("Hello.") 
        except Exception as e:
            raise HTTPException(status_code=503, 
                detail=f"Local LLM Error (503): Ensure Ollama is running and 'llama3' is pulled (try: ollama run llama3).")
    
    if llm is None:
        raise HTTPException(status_code=400, detail="Invalid LLM source selected or configuration missing.")
        
    # --- Memory Setup (Tier 3: Summary Buffer) ---
    if user_id not in SESSION_MEMORIES:
        
        memory = ConversationSummaryBufferMemory(
            llm=llm, 
            max_token_limit=8000, 
            memory_key="chat_history", 
            return_messages=True
        )
        SESSION_MEMORIES[user_id] = memory

        initial_persona_message = (
            "You are PyCoach, a patient, Socratic AI tutor specializing in Python Programming. "
            "Your goal is to guide the learner to the correct answer. You MUST adhere to the rules "
            "defined in the system prompt."
        )
        
        
        memory.chat_memory.add_message(SystemMessage(content=initial_persona_message))
        
    return llm, SESSION_MEMORIES[user_id]


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if GLOBAL_RETRIEVER is None:
        raise HTTPException(status_code=500, detail="RAG system is not initialized. Run `rag_pipeline.py` first.")
        
    # 1. Get LLM, Memory, and Profile
    start_time = time.time()
    try:
        llm, memory = get_llm_and_memory(request.user_id, request.api_key, request.llm_source)
    except HTTPException:
        # Re-raise explicit HTTP errors (like 503 Ollama error)
        raise 

    profile = get_student_profile(request.user_id)
    adaptive_prompt = get_adaptive_prompt(profile)

    # 2. The RAG Chain using LCEL
    context_retrieval_chain = RunnablePassthrough.assign(
        context=itemgetter("question") | GLOBAL_RETRIEVER
    )

    # Define the core chain structure: [Context + Question + Prompt] -> LLM
    rag_chain = context_retrieval_chain | adaptive_prompt | llm

    # 3. Preparing and Invoking the Chain
    history = memory.load_memory_variables({})["chat_history"]
    inputs = {
        "question": request.message,
        "chat_history": history 
    }

    try:
        result = rag_chain.invoke(inputs)
        tutor_response = result.content
        
    except Exception as e:
        # Catching  LLM rate limiting (429) or other API/chain errors
        error_msg = f"LLM Generation Failed. Error: {e}"
        if "429" in str(e) or "quota" in str(e).lower():
            error_msg = f"QUOTA EXCEEDED (429): The {request.llm_source} limit was hit. Switch to the Local LLM option."
        raise HTTPException(status_code=503, detail=error_msg)


    # 4. Apply DDA and Update Memory
    
    time_taken = time.time() - start_time
    
    
    # Save the conversation context
    memory.save_context({"input": request.message}, {"output": tutor_response})

    # 5. Prepare and Return Final Response
    return ChatResponse(
        response=tutor_response,
       
        current_level=profile.current_level,
        source_documents=[] # Simplification: Omitted source document tracking for brevity
    )


# --- Start Server ---
if __name__ == "__main__":
    # Ensure this runs in the correct directory (one level up from backend/)
    uvicorn.run(app, host="0.0.0.0", port=8000)
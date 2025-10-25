# backend/models.py

from pydantic import BaseModel, Field
from typing import List, Optional


ADAPTIVE_LEVELS = ["Beginner", "Intermediate", "Expert"]
# --------------------------------------------------------

# 1. Student Profile Model (Persistent Database Schema)
class StudentProfile(BaseModel):
    """
    Defines the data structure for the student's persistent memory.
    The level is the primary adaptive metric.
    """
    user_id: str
    
   
    current_level: str = Field(
        default="Beginner", 
        description="The student's adaptive difficulty level (Beginner, Intermediate, or Expert)."
    )
    
   

# 2. API Request Model (Input to /api/chat)
class ChatRequest(BaseModel):
    """
    Defines the required inputs for the main chat API endpoint, 
    including the user's current level for adaptive prompting.
    """
    user_id: str
    message: str
    
    # SECURITY FIX/ADAPTIVE LEVELING: We need the level from the frontend selector 
    current_level: str = Field(default="Beginner", description="The level selected by the user for adaptive prompting.")
    
    # Hybrid LLM Selection: Passed from the frontend dropdown
    
    llm_source: str = Field(default="Gemini API (Personal Key)") 
    
    # Hybrid Auth: User-provided key for paid/uninterrupted use
    api_key: Optional[str] = Field(default=None, description="Personal API key provided by the user.")

# 3. API Response Model (Output from /api/chat)
class ChatResponse(BaseModel):
    """
    Defines the output structure returned to the Streamlit frontend.
    """
    response: str
   
    current_level: str = Field(description="The final level used for the adaptive prompt.")
    
   
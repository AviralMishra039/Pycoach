# backend/db_manager.py

from .models import StudentProfile
from typing import Dict, Any

# --- MOCK PERSISTENT STORAGE ---
# In a production app, this dictionary would be replaced by database queries.
MOCK_STUDENT_PROFILES: Dict[str, StudentProfile] = {
    "demo_user": StudentProfile(
        user_id="demo_user",
        current_level="Intermediate",
        mastery_score=0.65,
        weak_topics=["File I/O", "Recursion"]
    ),
    # Any new user will get a default profile when first accessed.
}

def get_student_profile(user_id: str) -> StudentProfile:
    """
    Retrieves the student's profile from the mock database, 
    or initializes a new one if the user is new.
    """
    if user_id not in MOCK_STUDENT_PROFILES:
        # Initialize a new profile if the user_id is new
        profile = StudentProfile(user_id=user_id)
        MOCK_STUDENT_PROFILES[user_id] = profile
    
    return MOCK_STUDENT_PROFILES[user_id]

def save_student_profile(profile: StudentProfile):
    """Updates the student's profile in the mock database (persists state)."""
    
    MOCK_STUDENT_PROFILES[profile.user_id] = profile.model_copy()
    
   
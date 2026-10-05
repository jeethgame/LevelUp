import os
from dotenv import load_dotenv
load_dotenv("backend/.env")

from app.utils.firebase import db
from app.services.storage_service import save_active_roadmap, get_active_roadmap, save_student_profile, get_student_profile

test_uid = "test_user_verification_123"

# 1. Test student profile save and get
profile_data = {
    "name": "Alex Mercer",
    "education": "Bachelor's Degree",
    "skills": "Python, FastAPI, React, Docker",
    "interests": "Full Stack AI Development",
    "goals": "Become a Senior AI Engineer in 6 months",
    "experience": "2 years building web apps"
}
save_student_profile(test_uid, profile_data)
retrieved_profile = get_student_profile(test_uid)
assert retrieved_profile is not None
assert retrieved_profile["name"] == "Alex Mercer"
print("1. Firestore Profile Save & Read: SUCCESS! Name:", retrieved_profile["name"])

# 2. Test active roadmap save and get
career_dec = {
    "career": "Full Stack AI Engineer",
    "confidence": 92,
    "industry_demand": "trending"
}
roadmap_data = {
    "duration_months": 3,
    "roadmap": [
        {"phase": "Phase 1: Foundations", "duration": "Weeks 1-2", "status": "pending", "focus_skills": ["Python", "FastAPI"], "milestones": []}
    ]
}
save_active_roadmap(test_uid, career_dec, roadmap_data)
retrieved_roadmap = get_active_roadmap(test_uid)
assert retrieved_roadmap is not None
assert retrieved_roadmap["career_decision"]["career"] == "Full Stack AI Engineer"
print("2. Firestore Active Roadmap Save & Read: SUCCESS! Career:", retrieved_roadmap["career_decision"]["career"])

# Clean up test document
db.collection("users").document(test_uid).delete()
print("3. Test document cleaned up successfully!")

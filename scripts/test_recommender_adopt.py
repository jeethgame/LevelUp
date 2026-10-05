import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.services.storage_service import get_active_roadmap, get_student_profile, db

client = TestClient(app)
test_uid = "test_adopt_recommender_user"

# Mock plan
mock_plan = {
    "title": "Mastery Path: Fullstack AI Engineer",
    "target_career": "Fullstack AI Engineer",
    "summary": "Master fullstack web apps and LLM orchestration in 6 weeks",
    "match_score": 92,
    "readiness_score": 70,
    "weeks_to_readiness": 6,
    "weekly_hours": 12,
    "explainability": {
        "why_this_path": "Tailored for AI Engineering",
        "strengths_leveraged": ["React", "FastAPI"],
        "top_skill_gaps_addressed": ["LangChain", "VectorDB"]
    },
    "phases": [
        {
            "phase_number": 1,
            "phase_name": "Phase 1: Foundations",
            "timeline": "Weeks 1-2",
            "milestones": [
                {
                    "title": "FastAPI Microservices",
                    "skills": ["FastAPI", "Python Async"],
                    "resources": [{"title": "FastAPI Docs", "url": "https://fastapi.tiangolo.com", "type": "docs"}],
                    "checkpoint_project": "Build an async REST server"
                }
            ]
        }
    ]
}

res = client.post("/api/v1/recommend/adopt", json={"roadmap": mock_plan, "user_id": test_uid})
assert res.status_code == 200
data = res.json()
assert data["status"] == "success"
print("Adopt API returned success:", data)

# Verify Firestore active roadmap
rm = get_active_roadmap(test_uid)
assert rm is not None
assert rm["career_decision"]["career"] == "Fullstack AI Engineer"
assert len(rm["learning_roadmap"]["roadmap"]) == 1
print("Verified Firestore Roadmap stored:", rm["career_decision"]["career"])

# Verify Firestore student profile
prof = get_student_profile(test_uid)
assert prof is not None
assert prof["goals"] == "Fullstack AI Engineer"
print("Verified Firestore Student Profile stored:", prof["goals"], "| Skills:", prof["skills"])

# Clean up
db.collection("users").document(test_uid).delete()
print("Cleaned up test user successfully!")

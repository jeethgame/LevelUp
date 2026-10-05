import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.services.storage_service import get_active_roadmap, get_student_profile, db

client = TestClient(app)
test_uid = "test_e2e_gap_analyzer_user"

# 1. Simulate Skill Gap Analyzer adoption payload
gap_payload = {
    "roadmap_title": "Full Stack React Developer Roadmap",
    "user_id": test_uid,
    "gap_analysis": {
        "match_percentage": 68.0,
        "job_readiness_score": 75.0,
        "matched_skills": ["JavaScript", "HTML/CSS", "Git"],
        "missing_skills": ["React", "TypeScript", "Redux", "Tailwind CSS"],
        "learning_velocity": {
            "total_estimated_hours": 48,
            "weeks_to_readiness": 4.5,
            "roadmap": [
                {
                    "phase": "Phase 1: React & TypeScript Foundations",
                    "timeline": "Weeks 1-2",
                    "estimated_hours": 24,
                    "skills": ["React", "TypeScript"],
                    "skill_details": [
                        {
                            "name": "React",
                            "category": "Frontend",
                            "hours": 14,
                            "resources": [{"title": "React Docs", "url": "https://react.dev", "type": "docs", "duration": "5h"}]
                        },
                        {
                            "name": "TypeScript",
                            "category": "Languages",
                            "hours": 10,
                            "resources": [{"title": "TypeScript Handbook", "url": "https://typescriptlang.org", "type": "docs", "duration": "4h"}]
                        }
                    ]
                },
                {
                    "phase": "Phase 2: State Management & Styling",
                    "timeline": "Weeks 3-4",
                    "estimated_hours": 24,
                    "skills": ["Redux", "Tailwind CSS"],
                    "skill_details": [
                        {
                            "name": "Redux",
                            "category": "State Management",
                            "hours": 12,
                            "resources": []
                        }
                    ]
                }
            ]
        }
    }
}

print("=== 1. Testing POST /api/v1/adopt-roadmap (Skill Gap Analyzer) ===")
res = client.post("/api/v1/adopt-roadmap", json=gap_payload)
assert res.status_code == 200, f"Error: {res.text}"
data = res.json()
assert data["status"] == "ok"
print("-> Adopt Gap Roadmap Response:", data)

print("\n=== 2. Verifying Firestore Active Roadmap ===")
active_rm = get_active_roadmap(test_uid)
assert active_rm is not None
assert active_rm["career_decision"]["career"] == "Full Stack React Developer Roadmap"
assert len(active_rm["learning_roadmap"]["roadmap"]) == 2
print("-> Stored Career:", active_rm["career_decision"]["career"])
print("-> Stored Phases:", len(active_rm["learning_roadmap"]["roadmap"]))
print("-> Stored Demand:", active_rm["career_decision"]["industry_demand"])

print("\n=== 3. Verifying Firestore Student Profile ===")
profile = get_student_profile(test_uid)
assert profile is not None
assert profile["goals"] == "Full Stack React Developer Roadmap"
print("-> Stored Profile Goals:", profile["goals"])
print("-> Stored Profile Skills:", profile["skills"])

print("\n=== 4. Testing GET /api/career/roadmap?uid=... ===")
get_res = client.get(f"/api/career/roadmap?uid={test_uid}")
assert get_res.status_code == 200
get_data = get_res.json()
assert get_data["career_decision"]["career"] == "Full Stack React Developer Roadmap"
print("-> GET /api/career/roadmap retrieved active roadmap successfully!")

# Clean up
db.collection("users").document(test_uid).delete()
print("\n>>> ALL FIREBASE ADOPTION, STORAGE, AND RETRIEVAL TESTS PASSED 100%! <<<")

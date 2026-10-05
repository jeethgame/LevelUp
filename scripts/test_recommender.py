import os
from dotenv import load_dotenv
load_dotenv("backend/.env")
os.environ["FIREBASE_SERVICE_ACCOUNT_PATH"] = os.path.abspath("backend/firebase-service-account.json")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_conversational_plan():
    payload = {
        "goal": "Build fullstack AI applications with React and FastAPI in 6 weeks",
        "profile": {
            "current_skills": ["JavaScript", "Basic Python"],
            "experience_level": "Intermediate",
            "weekly_hours": 12,
            "learning_style": "Hands-on projects"
        }
    }
    res = client.post("/api/v1/recommend/conversational-plan", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    plan = data["plan"]
    assert "phases" in plan
    print("Plan generated successfully:", plan["title"], "| Total Phases:", len(plan["phases"]))

def test_explain():
    payload = {
        "item_type": "project",
        "item_title": "Build an Autonomous RAG Research Assistant",
        "goal": "Full-Stack AI Engineering",
        "learner_profile": {"current_skills": ["Python"]}
    }
    res = client.post("/api/v1/recommend/explain", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "explanation" in data
    print("Explainability test passed:", data["explanation"]["relevance_score"])

def test_diagnostic_quiz():
    payload = {"skill_name": "FastAPI", "difficulty": "intermediate"}
    res = client.post("/api/v1/recommend/diagnostic-quiz", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "quiz" in data
    print("Diagnostic Quiz test passed:", len(data["quiz"]["questions"]), "questions generated")

def test_generate_project():
    payload = {
        "domain": "AI Customer Support Agent",
        "milestone_title": "LangChain & Vector Database Integration",
        "skills": ["Python", "FastAPI", "ChromaDB"],
        "experience_level": "Intermediate"
    }
    res = client.post("/api/v1/recommend/generate-project", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "project" in data
    print("Project spec test passed:", data["project"]["project_title"])

def test_validate_checkpoint():
    payload = {
        "milestone_title": "Setup FastAPI Server",
        "checkpoint_goal": "Create modular FastAPI server with health endpoint and CORS",
        "submission_text": "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/health')\ndef h(): return {'ok': True}"
    }
    res = client.post("/api/v1/recommend/validate-checkpoint", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "evaluation" in data
    print("Checkpoint validation test passed:", data["evaluation"]["grade"])

if __name__ == "__main__":
    test_conversational_plan()
    test_explain()
    test_diagnostic_quiz()
    test_generate_project()
    test_validate_checkpoint()
    print(">>> ALL BACKEND RECOMMENDER TESTS PASSED CLEANLY! <<<")

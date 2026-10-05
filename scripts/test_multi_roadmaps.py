import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.services.storage_service import (
    save_roadmap_to_library,
    list_user_roadmaps,
    switch_active_roadmap,
    delete_roadmap_from_library,
    get_active_roadmap,
    db
)

client = TestClient(app)
test_uid = "test_multi_roadmaps_user_777"

# Clean any existing test records
try:
    for doc in db.collection("users").document(test_uid).collection("roadmaps").stream():
        doc.reference.delete()
    db.collection("users").document(test_uid).delete()
except Exception:
    pass

print("=== 1. Creating Roadmap 1: Full Stack AI Engineer ===")
rm1_career = {
    "career": "Full Stack AI Engineer",
    "confidence": 94,
    "industry_demand": "trending",
    "time_to_job_ready": "6 weeks"
}
rm1_roadmap = {
    "duration_months": 2,
    "roadmap": [
        {"phase": "Phase 1: FastAPI & LangChain", "duration": "Weeks 1-2", "status": "completed"},
        {"phase": "Phase 2: RAG Microservices", "duration": "Weeks 3-4", "status": "pending"}
    ]
}
id1 = save_roadmap_to_library(test_uid, rm1_career, rm1_roadmap, title="Full Stack AI Engineer", is_active=True)
print("-> Roadmap 1 Created ID:", id1)

print("\n=== 2. Creating Roadmap 2: Cloud DevOps Pro ===")
rm2_career = {
    "career": "Cloud DevOps Pro",
    "confidence": 88,
    "industry_demand": "stable",
    "time_to_job_ready": "8 weeks"
}
rm2_roadmap = {
    "duration_months": 3,
    "roadmap": [
        {"phase": "Phase 1: Docker & Kubernetes", "duration": "Weeks 1-3", "status": "pending"},
        {"phase": "Phase 2: Terraform & AWS", "duration": "Weeks 4-6", "status": "pending"}
    ]
}
id2 = save_roadmap_to_library(test_uid, rm2_career, rm2_roadmap, title="Cloud DevOps Pro", is_active=True)
print("-> Roadmap 2 Created ID:", id2)

print("\n=== 3. Testing GET /api/career/roadmaps ===")
res_list = client.get(f"/api/career/roadmaps?uid={test_uid}")
assert res_list.status_code == 200
roadmaps_list = res_list.json()
print("-> Total roadmaps returned:", len(roadmaps_list))
assert len(roadmaps_list) == 2
titles = [r["title"] for r in roadmaps_list]
print("-> Roadmap titles:", titles)
assert "Full Stack AI Engineer" in titles
assert "Cloud DevOps Pro" in titles

print("\n=== 4. Checking Active Roadmap ===")
active = get_active_roadmap(test_uid)
print("-> Currently Active:", active["career_decision"]["career"])
assert active["career_decision"]["career"] == "Cloud DevOps Pro"

print("\n=== 5. Testing POST /api/career/roadmaps/switch/{roadmap_id} ===")
switch_res = client.post(f"/api/career/roadmaps/switch/{id1}?uid={test_uid}")
assert switch_res.status_code == 200
switched_active = get_active_roadmap(test_uid)
print("-> Switched Active to:", switched_active["career_decision"]["career"])
assert switched_active["career_decision"]["career"] == "Full Stack AI Engineer"

print("\n=== 6. Testing DELETE /api/career/roadmaps/{roadmap_id} ===")
del_res = client.delete(f"/api/career/roadmaps/{id2}?uid={test_uid}")
assert del_res.status_code == 200
remaining = list_user_roadmaps(test_uid)
print("-> Remaining roadmaps count:", len(remaining))
assert len(remaining) == 1
assert remaining[0]["id"] == id1

# Clean up
try:
    for doc in db.collection("users").document(test_uid).collection("roadmaps").stream():
        doc.reference.delete()
    db.collection("users").document(test_uid).delete()
except Exception:
    pass

print("\n>>> ALL MULTI-ROADMAP STORAGE & RETRIEVAL TESTS PASSED 100%! <<<")

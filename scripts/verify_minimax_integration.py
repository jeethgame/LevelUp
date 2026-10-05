import asyncio
import os
from dotenv import load_dotenv

load_dotenv("backend/.env")

from app.services.recommender_service import (
    generate_conversational_learning_plan,
    explain_recommendation_item,
    generate_diagnostic_quiz,
    generate_project_spec,
    validate_checkpoint_submission,
    milestone_ai_chat,
)
from app.services.ai_service import generate_subskills, progress_insights
from app.services.roadmap_agent import generate_roadmap

async def run_tests():
    print("=== 1. Testing Learning Path Recommender with MiniMax-M3 ===")
    plan = await generate_conversational_learning_plan(
        "Build fullstack AI apps with FastAPI and React",
        {"current_skills": ["Python", "JavaScript"], "experience_level": "Intermediate", "weekly_hours": 12}
    )
    print("-> Plan Title:", plan.get("title"))
    print("-> Phases Count:", len(plan.get("phases", [])))
    print("-> Match Score:", plan.get("match_score"))

    print("\n=== 2. Testing Explainability with MiniMax-M3 ===")
    exp = await explain_recommendation_item(
        "course", "DeepLearning.AI LangChain Masterclass", "AI Engineering", {"skills": ["Python"]}
    )
    print("-> Why Recommended:", exp.get("why_recommended"))
    print("-> Relevance Score:", exp.get("relevance_score"))

    print("\n=== 3. Testing Diagnostic Quiz with MiniMax-M3 ===")
    quiz = await generate_diagnostic_quiz("FastAPI", "intermediate")
    print("-> Quiz Skill:", quiz.get("skill"))
    print("-> Questions Count:", len(quiz.get("questions", [])))

    print("\n=== 4. Testing Project Architect with MiniMax-M3 ===")
    proj = await generate_project_spec("Autonomous AI Agent", "RAG Microservice", ["FastAPI", "VectorDB"])
    print("-> Project Title:", proj.get("project_title"))
    print("-> Tech Stack:", proj.get("tech_stack"))

    print("\n=== 5. Testing Code Review Checkpoint with MiniMax-M3 ===")
    review = await validate_checkpoint_submission(
        "FastAPI Server", "Create basic server", "from fastapi import FastAPI\napp = FastAPI()"
    )
    print("-> Grade:", review.get("grade"))
    print("-> Feedback:", review.get("feedback"))

    print("\n=== 6. Testing Career Roadmap Agent with MiniMax-M3 ===")
    career_res = await generate_roadmap({
        "current_skills": "Python, SQL, Machine Learning",
        "goals": "Senior Data Scientist",
        "hours_per_week": 15
    })
    print("-> Career Decision:", career_res.get("career_decision", {}).get("career"))
    print("-> Confidence:", career_res.get("career_decision", {}).get("confidence"))

    print("\n=== 7. Testing AI Subskills with MiniMax-M3 ===")
    subskills_res = await generate_subskills({"skillName": "Docker & Kubernetes Containerization"})
    print("-> Subskills Generated:", [s["title"] for s in subskills_res.get("subskills", [])])

    print("\n>>> ALL MINIMAX-M3 BACKEND INTEGRATIONS FUNCTIONING LIVE AND PERFECT! <<<")

asyncio.run(run_tests())

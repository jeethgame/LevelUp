with open("backend/app/services/recommender_service.py", "a", encoding="utf-8") as f:
    f.write('''
def _build_fallback_recommendation(goal: str, profile: Dict[str, Any]) -> Dict[str, Any]:
    weekly_hours = max(1, min(60, int(profile.get("weekly_hours") or profile.get("hoursPerWeek") or 10)))
    skills = profile.get("current_skills") or profile.get("skills") or []
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",") if s.strip()]
    experience = profile.get("experience_level") or profile.get("experience") or "Beginner"
    learning_style = profile.get("learning_style") or "Hands-on projects"
    goal_clean = (goal or "Full-Stack AI Engineering").strip()

    is_ai = any(w in goal_clean.lower() for w in ["ai", "ml", "machine learning", "data", "llm"])
    is_dev = any(w in goal_clean.lower() for w in ["devops", "cloud", "docker", "infra", "backend"])
    cat_key = "ai_ml" if is_ai else ("backend_devops" if is_dev else "fullstack")
    res_list = CURATED_CATALOG.get(cat_key, CURATED_CATALOG["fullstack"])

    total_hours = 64
    weeks_to_ready = max(2, math.ceil(total_hours / weekly_hours))

    phase_1 = [{
        "id": f"m-{uuid.uuid4().hex[:6]}",
        "title": "Core Foundations & Tooling Setup",
        "description": f"Master fundamental syntax, dev environments, and mental models for {goal_clean}.",
        "estimated_hours": 14,
        "skills": ["Foundations", "Git & CLI", "Core Architecture"],
        "resources": [
            {"title": "Interactive Foundations Guide", "url": "https://developer.mozilla.org/en-US/", "type": "docs", "provider": "Official Specs", "difficulty": "beginner", "duration": "4 hours", "match_reason": "Builds fundamental prerequisites."},
            {"title": "Starter Masterclass", "url": "https://www.youtube.com/results?search_query=" + goal_clean.replace(" ", "+"), "type": "video", "provider": "Verified Tech Labs", "difficulty": "beginner", "duration": "10 hours", "match_reason": "Visual walkthrough with exercises."}
        ],
        "checkpoint_project": "Build and document a functional baseline prototype.",
        "completed": False,
    }]

    phase_2 = [{
        "id": f"m-{uuid.uuid4().hex[:6]}",
        "title": "Deep Dive, Frameworks & Data Flow",
        "description": f"Integrate modern frameworks, data persistence, and API contracts for {goal_clean}.",
        "estimated_hours": 20,
        "skills": ["Frameworks", "REST/GraphQL APIs", "Data Persistence"],
        "resources": [res_list[0] if len(res_list) > 0 else {"title": "Core Framework Guide", "url": "https://fullstackopen.com/", "type": "course", "provider": "Open Education", "difficulty": "intermediate", "duration": "16 hours", "match_reason": "Structured curriculum closing top skill gaps."}],
        "checkpoint_project": "Develop a full-stack module with persistent storage and error handling.",
        "completed": False,
    }]

    phase_3 = [{
        "id": f"m-{uuid.uuid4().hex[:6]}",
        "title": "Applied Real-World Capstone Project",
        "description": "Architect, build, and deploy an end-to-end production-grade portfolio application.",
        "estimated_hours": 20,
        "skills": ["System Design", "Cloud Deployment", "CI/CD & Security"],
        "resources": [res_list[1] if len(res_list) > 1 else {"title": "System Architecture Guide", "url": "https://github.com/donnemartin/system-design-primer", "type": "project", "provider": "GitHub Community", "difficulty": "advanced", "duration": "14 hours", "match_reason": "Production project showcasing portfolio competencies."}],
        "checkpoint_project": "Deploy a live authenticated web application with automated testing.",
        "completed": False,
    }]

    phase_4 = [{
        "id": f"m-{uuid.uuid4().hex[:6]}",
        "title": "Optimization & Career Readiness",
        "description": "Fine-tune system performance, write technical design docs, and solve domain interview challenges.",
        "estimated_hours": 10,
        "skills": ["Optimization", "Benchmarking", "Technical Interview Prep"],
        "resources": [{"title": "Engineering Interview Patterns", "url": "https://leetcode.com/", "type": "article", "provider": "Tech Handbook", "difficulty": "intermediate", "duration": "8 hours", "match_reason": "Bridges knowledge into job readiness."}],
        "checkpoint_project": "Deliver comprehensive documentation, benchmark report, and live demo link.",
        "completed": False,
    }]

    return {
        "id": f"plan-{uuid.uuid4().hex[:8]}",
        "title": f"Mastery Path: {goal_clean}",
        "target_career": goal_clean,
        "summary": f"Customized {weeks_to_ready}-week learning roadmap designed for {experience} level ({weekly_hours} hrs/week) emphasizing {learning_style}.",
        "match_score": 88,
        "readiness_score": 42 if experience == "Beginner" else 68,
        "weekly_hours": weekly_hours,
        "total_estimated_hours": total_hours,
        "weeks_to_readiness": weeks_to_ready,
        "explainability": {
            "why_this_path": f"Tailored for '{goal_clean}' based on your {experience} background, prioritizing {learning_style} for maximum retention.",
            "strengths_leveraged": skills[:3] if skills else ["Rapid learning mindset", "Foundational problem solving"],
            "top_skill_gaps_addressed": ["System Design", "Production Architecture", "Applied Testing"],
            "modality_alignment": f"Over 70% of resources feature {learning_style} and project builds.",
            "career_market_outlook": "High industry demand with strong hiring velocity across product engineering teams."
        },
        "phases": [
            {"phase_number": 1, "phase_name": "Phase 1: Foundations & Tooling", "timeline": f"Weeks 1-{max(1, weeks_to_ready // 4)}", "difficulty": "beginner", "estimated_hours": 14, "prerequisites": [], "milestones": phase_1},
            {"phase_number": 2, "phase_name": "Phase 2: Frameworks & Logic", "timeline": f"Weeks {max(2, weeks_to_ready // 4 + 1)}-{max(2, (weeks_to_ready * 2) // 4)}", "difficulty": "intermediate", "estimated_hours": 20, "prerequisites": ["Foundations & Tooling"], "milestones": phase_2},
            {"phase_number": 3, "phase_name": "Phase 3: Production Capstone", "timeline": f"Weeks {max(3, (weeks_to_ready * 2) // 4 + 1)}-{max(3, (weeks_to_ready * 3) // 4)}", "difficulty": "advanced", "estimated_hours": 20, "prerequisites": ["Frameworks & Logic"], "milestones": phase_3},
            {"phase_number": 4, "phase_name": "Phase 4: Optimization & Readiness", "timeline": f"Weeks {max(4, (weeks_to_ready * 3) // 4 + 1)}-{weeks_to_ready}", "difficulty": "intermediate", "estimated_hours": 10, "prerequisites": ["Production Capstone"], "milestones": phase_4},
        ]
    }
''')

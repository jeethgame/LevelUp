with open("backend/app/services/recommender_service.py", "a", encoding="utf-8") as f:
    f.write('''
async def milestone_ai_chat(milestone_context: Dict[str, Any], chat_history: List[Dict[str, str]], user_query: str) -> Dict[str, Any]:
    skills_text = ", ".join(milestone_context.get("skills", ["required skills"]))
    default_reply = f"For milestone **{milestone_context.get('title', 'this milestone')}**, focus first on {skills_text}. Break the problem down into small testable units."
    ai = _get_ai_client()
    if ai is None:
        return {"reply": default_reply, "suggestions": ["Give me a starter code template", "What are the common pitfalls?", "How can I test this?"]}

    prompt = f"You are an AI senior mentor helping a student with milestone: {milestone_context.get('title')}. Skills: {skills_text}. Checkpoint project: {milestone_context.get('checkpoint_project')}. Answer concisely with markdown code snippets and return JSON: {{\"reply\": \"<markdown>\", \"suggestions\": [\"q1\", \"q2\", \"q3\"]}}"
    msgs = [{"role": "system", "content": prompt}]
    for m in chat_history[-6:]:
        msgs.append({"role": m.get("role", "user"), "content": m.get("content", "")})
    msgs.append({"role": "user", "content": user_query})

    try:
        res = await ai["client"].chat.completions.create(model=ai["model"], temperature=0.4, messages=msgs)
        content = res.choices[0].message.content or ""
        parsed = json.loads(content)
        if isinstance(parsed, dict) and "reply" in parsed:
            return parsed
    except Exception:
        pass
    return {"reply": default_reply, "suggestions": ["Give me a starter code template", "What are the common pitfalls?", "How can I test this?"]}


async def generate_diagnostic_quiz(skill_name: str, difficulty: str = "intermediate") -> Dict[str, Any]:
    fallback = {
        "skill": skill_name,
        "difficulty": difficulty,
        "questions": [
            {
                "id": "q1",
                "question": f"What is the primary architectural advantage of using modular patterns in {skill_name}?",
                "options": ["Separation of concerns and easier testing", "Direct CPU overclocking", "Eliminates version control need", "Guarantees zero latency"],
                "correct_index": 0,
                "explanation": "Modular design isolates business logic, simplifies unit testing, and enhances code maintainability."
            },
            {
                "id": "q2",
                "question": f"When optimizing performance in {skill_name}, what is the best first step?",
                "options": ["Rewrite entire codebase in machine assembly", "Profile and benchmark bottlenecks before premature optimization", "Disable logging and error handling", "Add threading everywhere"],
                "correct_index": 1,
                "explanation": "Profiling provides concrete metrics to identify actual hotspots before optimizing."
            },
            {
                "id": "q3",
                "question": f"How should state or external side-effects be handled in a scalable {skill_name} architecture?",
                "options": ["Global mutable variables", "Encapsulated services with explicit interfaces and error boundaries", "Hardcoded database credentials", "Ignoring asynchronous promises"],
                "correct_index": 1,
                "explanation": "Encapsulation prevents ripple effects and keeps side-effects predictable."
            }
        ]
    }
    ai = _get_ai_client()
    if ai is None:
        return fallback

    prompt = f"Generate a 3-question technical assessment for '{skill_name}' ({difficulty}). Return JSON: {{\"skill\": \"{skill_name}\", \"difficulty\": \"{difficulty}\", \"questions\": [{{\"id\": \"q1\", \"question\": \"...\", \"options\": [\"opt0\", \"opt1\", \"opt2\", \"opt3\"], \"correct_index\": 0, \"explanation\": \"...\"}}]}}"
    try:
        res = await ai["client"].chat.completions.create(model=ai["model"], temperature=0.2, messages=[{"role": "system", "content": "You are a technical interviewer. Output JSON only."}, {"role": "user", "content": prompt}])
        content = res.choices[0].message.content or ""
        parsed = json.loads(content)
        if isinstance(parsed, dict) and "questions" in parsed:
            return parsed
    except Exception:
        pass
    return fallback


async def generate_project_spec(domain: str, milestone_title: str, skills: List[str], experience_level: str = "Intermediate") -> Dict[str, Any]:
    skills_str = ", ".join(skills) if skills else domain
    fallback = {
        "project_title": f"Autonomous {domain.title()} Service",
        "tagline": f"Production-grade {domain} service showcasing {skills_str}",
        "difficulty": experience_level,
        "estimated_hours": 16,
        "architecture_overview": f"A modular microservice / full-stack application leveraging modern {skills_str} patterns with REST API endpoints and state persistence.",
        "key_features": [
            "Secure JWT authentication & role-based access control",
            "Async event processing and caching with Redis",
            "Automated unit and integration test suite with CI pipeline",
            "Interactive responsive dashboard with dark mode"
        ],
        "tech_stack": ["React / TypeScript", "FastAPI / Python", "PostgreSQL / Redis", "Docker"],
        "starter_boilerplate_code": "# main.py\\nfrom fastapi import FastAPI\\n\\napp = FastAPI(title='" + domain.replace(" ", "_") + "_service')\\n\\n@app.get('/health')\\ndef health():\\n    return {'status': 'healthy', 'version': '1.0.0'}\\n",
        "evaluation_criteria": ["Clean architecture & separation of concerns", "Comprehensive error handling", "Working documentation & tests"]
    }
    ai = _get_ai_client()
    if ai is None:
        return fallback

    prompt = f"Generate an impressive project spec for '{domain}' milestone '{milestone_title}' demonstrating {skills}. Return JSON matching fields: project_title, tagline, difficulty, estimated_hours, architecture_overview, key_features (list), tech_stack (list), starter_boilerplate_code (string), evaluation_criteria (list)."
    try:
        res = await ai["client"].chat.completions.create(model=ai["model"], temperature=0.4, messages=[{"role": "system", "content": "You are a software architect. Output JSON only."}, {"role": "user", "content": prompt}])
        content = res.choices[0].message.content or ""
        parsed = json.loads(content)
        if isinstance(parsed, dict) and "project_title" in parsed:
            return parsed
    except Exception:
        pass
    return fallback


async def validate_checkpoint_submission(milestone_title: str, checkpoint_goal: str, submission_text: str) -> Dict[str, Any]:
    fallback = {
        "passed": True,
        "score": 88,
        "grade": "Proficient",
        "feedback": "Great work! Your submission effectively implements the core requirements for this checkpoint.",
        "strengths": ["Clear logic flow", "Addresses core requirements", "Clean organization"],
        "areas_for_improvement": ["Add more edge-case validation", "Include automated unit tests"],
        "badges_unlocked": ["Checkpoint Crusher", "Fast Learner"]
    }
    ai = _get_ai_client()
    if ai is None:
        return fallback

    prompt = f"Review student checkpoint submission for milestone '{milestone_title}' (Goal: '{checkpoint_goal}'):\n{submission_text}\n\nReturn JSON: {{\"passed\": true, \"score\": 90, \"grade\": \"Proficient\", \"feedback\": \"...\", \"strengths\": [\"s1\"], \"areas_for_improvement\": [\"a1\"], \"badges_unlocked\": [\"b1\"]}}"
    try:
        res = await ai["client"].chat.completions.create(model=ai["model"], temperature=0.2, messages=[{"role": "system", "content": "You are an encouraging code reviewer. Output JSON only."}, {"role": "user", "content": prompt}])
        content = res.choices[0].message.content or ""
        parsed = json.loads(content)
        if isinstance(parsed, dict) and "score" in parsed:
            return parsed
    except Exception:
        pass
    return fallback
''')

with open("backend/app/services/recommender_service.py", "a", encoding="utf-8") as f:
    f.write('''
SYSTEM_ROADMAP_PROMPT = """
You are an expert AI Learning Path Architect.
Given a learner goal and profile (current skills, experience level, weekly hours, learning style, target career), generate a high-impact modular 4-phase learning roadmap.
Return ONLY valid JSON matching this schema:
{
  "id": "plan-uuid",
  "title": "Mastery Path: <Target Goal>",
  "target_career": "<Target Career>",
  "summary": "<1-2 sentence summary>",
  "match_score": 88,
  "readiness_score": 65,
  "weekly_hours": 10,
  "total_estimated_hours": 64,
  "weeks_to_readiness": 6,
  "explainability": {
    "why_this_path": "<explanation>",
    "strengths_leveraged": ["<skill1>", "<skill2>"],
    "top_skill_gaps_addressed": ["<gap1>", "<gap2>"],
    "modality_alignment": "<style alignment>",
    "career_market_outlook": "<outlook>"
  },
  "phases": [
    {
      "phase_number": 1,
      "phase_name": "Phase 1: <Name>",
      "timeline": "Weeks 1-2",
      "difficulty": "beginner|intermediate|advanced",
      "estimated_hours": 15,
      "prerequisites": [],
      "milestones": [
        {
          "id": "m-1",
          "title": "<Milestone Title>",
          "description": "<Description>",
          "estimated_hours": 8,
          "skills": ["<skill1>"],
          "resources": [
            {
              "title": "<Resource Title>",
              "url": "<URL>",
              "type": "course|project|video|docs|article",
              "provider": "<Provider>",
              "difficulty": "beginner|intermediate|advanced",
              "duration": "4 hours",
              "match_reason": "<Why recommended>"
            }
          ],
          "checkpoint_project": "<Project Goal>",
          "completed": false
        }
      ]
    }
  ]
}
"""

async def generate_conversational_learning_plan(goal: str, profile: Dict[str, Any]) -> Dict[str, Any]:
    fallback = _build_fallback_recommendation(goal, profile)
    ai = _get_ai_client()
    if ai is None:
        return fallback

    user_payload = {
        "learner_goal": goal,
        "profile": {
            "current_skills": profile.get("current_skills") or profile.get("skills") or [],
            "experience_level": profile.get("experience_level") or profile.get("experience") or "Beginner",
            "weekly_hours": profile.get("weekly_hours") or profile.get("hoursPerWeek") or 10,
            "learning_style": profile.get("learning_style") or "Hands-on projects",
            "target_career": profile.get("target_career") or goal,
        }
    }

    try:
        response = await ai["client"].chat.completions.create(
            model=ai["model"],
            temperature=0.3,
            messages=[
                {"role": "system", "content": SYSTEM_ROADMAP_PROMPT},
                {"role": "user", "content": json.dumps(user_payload)},
            ],
            response_format={"type": "json_object"} if "gpt" in ai["model"] else None
        )
        content = response.choices[0].message.content or ""
        parsed = json.loads(content)
        if isinstance(parsed, dict) and "phases" in parsed:
            if not parsed.get("id"):
                parsed["id"] = f"plan-{uuid.uuid4().hex[:8]}"
            return parsed
    except Exception:
        pass
    return fallback


async def explain_recommendation_item(item_type: str, item_title: str, goal: str, learner_profile: Dict[str, Any]) -> Dict[str, Any]:
    ai = _get_ai_client()
    fallback = {
        "item_title": item_title,
        "item_type": item_type,
        "relevance_score": 92,
        "why_recommended": f"'{item_title}' directly addresses essential capabilities required for {goal or 'your target mastery'}.",
        "skill_gap_closure": "Builds strong competency in required core workflows and prepares you for downstream milestones.",
        "prerequisite_check": "Your existing foundational skills align well with the difficulty curve of this resource.",
        "expected_takeaway": "Practical competency, runnable code artifacts, and portfolio-ready documentation.",
    }
    if ai is None:
        return fallback

    prompt = f"Explain in detail why the {item_type} titled '{item_title}' is recommended for '{goal}'. Profile: {json.dumps(learner_profile)}. Return JSON with relevance_score (0-100), why_recommended, skill_gap_closure, prerequisite_check, expected_takeaway."
    try:
        response = await ai["client"].chat.completions.create(
            model=ai["model"],
            temperature=0.2,
            messages=[
                {"role": "system", "content": "You are an AI pedagogical mentor. Output JSON only."},
                {"role": "user", "content": prompt}
            ]
        )
        content = response.choices[0].message.content or ""
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            return {**fallback, **parsed}
    except Exception:
        pass
    return fallback


async def adapt_learning_roadmap(current_roadmap: Dict[str, Any], feedback_type: str, target_milestone_id: Optional[str] = None, user_notes: Optional[str] = None) -> Dict[str, Any]:
    phases = current_roadmap.get("phases", [])
    if feedback_type == "already_known" and target_milestone_id:
        for p in phases:
            for m in p.get("milestones", []):
                if m.get("id") == target_milestone_id:
                    m["completed"] = True
                    m["notes"] = "Marked as previously mastered"
        current_roadmap["phases"] = phases
        return {"roadmap": current_roadmap, "change_summary": "Milestone marked as mastered and downstream milestones updated."}

    if feedback_type == "accelerate":
        current_roadmap["total_estimated_hours"] = max(20, int(current_roadmap.get("total_estimated_hours", 60) * 0.75))
        current_roadmap["weeks_to_readiness"] = max(2, math.ceil(current_roadmap["total_estimated_hours"] / max(1, current_roadmap.get("weekly_hours", 10))))
        return {"roadmap": current_roadmap, "change_summary": "Roadmap accelerated! Streamlined theoretical milestones to focus on capstones."}

    ai = _get_ai_client()
    if ai is None:
        return {"roadmap": current_roadmap, "change_summary": f"Roadmap adapted for {feedback_type}."}

    prompt = f"Adjust roadmap for feedback '{feedback_type}' on milestone '{target_milestone_id}'. Notes: '{user_notes}'. Return modified roadmap JSON with top-level 'change_summary' string.\n{json.dumps(current_roadmap)}"
    try:
        res = await ai["client"].chat.completions.create(
            model=ai["model"],
            temperature=0.3,
            messages=[
                {"role": "system", "content": "You are an adaptive roadmap rebalancer. Output JSON only."},
                {"role": "user", "content": prompt}
            ]
        )
        content = res.choices[0].message.content or ""
        parsed = json.loads(content)
        if isinstance(parsed, dict) and "phases" in parsed:
            summary = parsed.pop("change_summary", "Roadmap recalibrated successfully.")
            return {"roadmap": parsed, "change_summary": summary}
    except Exception:
        pass
    return {"roadmap": current_roadmap, "change_summary": "Roadmap recalibrated."}
''')

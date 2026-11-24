import json
import os
import re
from typing import Any, Dict, List, Optional
import urllib.request
from app.services.llm_client import get_client, parse_llm_json

CHAT_SYSTEM_PROMPT = """You are LevelUP AI Assistant — an expert career coach, coding mentor, and system design reviewer.

You have access to the user's learning context (skills, tasks, roadmaps) provided below.

Your capabilities:
1. **Mentorship**: Concise, encouraging advice on coding, DSA, system design, and career growth.
2. **Workspace Actions**: Use the provided tools to create/update/delete tasks and skills when the user asks. You can chain multiple tool calls in one turn.
3. **Vision & GitHub**: Analyze architecture diagrams, code screenshots, and GitHub repos.

Guidelines:
- Use markdown formatting in your replies (bullets, bold, code blocks).
- When updating tasks/skills, match by title from the context provided.
- Be encouraging, technical yet accessible.
- After answering, suggest 2-3 follow-up questions the user might ask.
"""

AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new task on the user's Kanban board",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title"},
                    "priority": {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"], "description": "Task priority"},
                    "status": {"type": "string", "enum": ["NOT_STARTED", "IN_PROGRESS", "COMPLETED"], "description": "Initial status"},
                    "deadline": {"type": "string", "description": "Deadline in YYYY-MM-DDTHH:MM:SS format, or null"},
                    "notes": {"type": "string", "description": "Optional notes"},
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_task_status",
            "description": "Move a task to a different status column (To Do, In Progress, Completed)",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_title": {"type": "string", "description": "Title of the task to update"},
                    "status": {"type": "string", "enum": ["NOT_STARTED", "IN_PROGRESS", "COMPLETED"]},
                },
                "required": ["task_title", "status"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_task_priority",
            "description": "Change a task's priority level",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_title": {"type": "string", "description": "Title of the task to update"},
                    "priority": {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"]},
                },
                "required": ["task_title", "priority"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task from the board",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_title": {"type": "string", "description": "Title of the task to delete"},
                },
                "required": ["task_title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_skill",
            "description": "Add a new skill to the user's portfolio",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Skill name"},
                    "category_name": {"type": "string", "description": "Category to file the skill under"},
                    "priority": {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"]},
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_skill_progress",
            "description": "Update a skill's progress percentage",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill_name": {"type": "string", "description": "Name of the skill"},
                    "progress": {"type": "integer", "minimum": 0, "maximum": 100, "description": "New progress value"},
                },
                "required": ["skill_name", "progress"],
            },
        },
    },
]

# Maps tool call names to the action format the frontend already understands
def _tool_call_to_action(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    if name == "create_task":
        return {
            "type": "CREATE_TASK",
            "data": {
                "title": args.get("title", ""),
                "priority": args.get("priority", "MEDIUM"),
                "status": args.get("status", "NOT_STARTED"),
                "deadline": args.get("deadline"),
                "notes": args.get("notes", ""),
            },
        }
    if name == "update_task_status":
        return {
            "type": "UPDATE_TASK_STATUS",
            "data": {
                "taskTitle": args.get("task_title", ""),
                "status": args.get("status", "IN_PROGRESS"),
            },
        }
    if name == "update_task_priority":
        return {
            "type": "UPDATE_TASK_PRIORITY",
            "data": {
                "taskTitle": args.get("task_title", ""),
                "priority": args.get("priority", "MEDIUM"),
            },
        }
    if name == "delete_task":
        return {
            "type": "DELETE_TASK",
            "data": {"taskTitle": args.get("task_title", "")},
        }
    if name == "create_skill":
        return {
            "type": "CREATE_SKILL",
            "data": {
                "title": args.get("title", ""),
                "categoryName": args.get("category_name", "General"),
                "priority": args.get("priority", "MEDIUM"),
                "progress": 0,
            },
        }
    if name == "update_skill_progress":
        return {
            "type": "UPDATE_SKILL_PROGRESS",
            "data": {
                "skillName": args.get("skill_name", ""),
                "progress": args.get("progress", 0),
            },
        }
    return {"type": name.upper(), "data": args}

def _fetch_github_repo_summary(url: str) -> Optional[str]:
    """Extract owner/repo and fetch public repository metadata."""
    match = re.search(r"github\.com/([^/]+)/([^/]+)", url)
    if not match:
        return None
    owner, repo = match.group(1), match.group(2).replace(".git", "")
    # Validate: only allow github.com API calls (prevent SSRF)
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    try:
        req = urllib.request.Request(api_url, headers={"User-Agent": "LevelUP-Agent"})
        with urllib.request.urlopen(req, timeout=3) as resp:  # noqa: S310
            data = json.load(resp)  # FIX: decode response before reading fields
            full_name = data.get('full_name', f"{owner}/{repo}")
            desc = data.get('description', 'No description')
            lang = data.get('language', 'N/A')
            topics = ', '.join(data.get('topics', []))
            stars = data.get('stargazers_count', 0)
            return f"GitHub Repo: {full_name}\nDescription: {desc}\nLanguage: {lang}\nTopics: {topics}\nStars: {stars}"
    except Exception:
        return f"GitHub Repository: {owner}/{repo}"



def _smart_fallback_response(query: str, context: Dict[str, Any]) -> Dict[str, Any]:
    q = query.lower()
    tracked_skills = context.get('trackedSkills') or []
    tasks = context.get('tasks') or []

    actions = []
    follow_ups = [
        "What should I learn next?",
        "Add a high-priority task for tomorrow",
        "Give me a mock interview question"
    ]

    # 1. Detect Task Creation
    if re.search(r'\b(?:add|create|new|schedule|remind)\b.*\b(?:task|todo|to-do|item)\b', q) or 'add a task' in q or 'create a task' in q:
        title = re.sub(r'^(?:please\s+)?(?:can you\s+)?(?:add|create|new|schedule)\s+(?:a\s+)?(?:(?:high|medium|low)\s+)?(?:priority\s+)?(?:task|todo|to-do)?(?:\s+for\s+me|\s+for|\s+to|\s*:)?\s*', '', query, flags=re.IGNORECASE).strip(' "\':-')
        priority = 'HIGH' if 'high' in q else 'LOW' if 'low' in q else 'MEDIUM'
        status = 'IN_PROGRESS' if any(w in q for w in ['current', 'in progress', 'today', 'now']) else 'NOT_STARTED'

        deadline = None
        if 'tomorrow' in q:
            from datetime import datetime, timedelta
            deadline = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%dT18:00:00')

        if not title:
            title = "Review learning goals and milestones"

        actions.append({
            'type': 'CREATE_TASK',
            'data': {
                'title': title,
                'priority': priority,
                'status': status,
                'deadline': deadline,
                'notes': f'Created via LevelUP AI Assistant'
            }
        })
        return {
            'reply': f"✅ Added **{title}** to your **{'Current (In Progress)' if status == 'IN_PROGRESS' else 'To Do'}** board with **{priority}** priority!",
            'actions': actions,
            'suggestedFollowUps': [
                "Show my current tasks",
                "Add another task for tomorrow",
                "What skills should I learn next?"
            ]
        }

    # 2. General Fallback
    skill_names = [s.get('name') for s in tracked_skills[:3] if s.get('name')]
    skills_context = f" I see you're working on **{', '.join(skill_names)}**." if skill_names else ""
    return {
        'reply': f"👋 I'm your **LevelUP AI Career & Study Assistant**.{skills_context}\n\nI can help you:\n- **Analyze architecture diagrams and GitHub repos** for best practices\n- **Auto-schedule and organize tasks** on your Kanban board\n- **Update your skills and progress** in real-time\n- **Practice technical interview questions**\n\nWhat would you like to work on right now?",
        'actions': [],
        'suggestedFollowUps': follow_ups
    }


def _build_llm_messages(
    messages: List[Dict[str, Any]],
    context: Dict[str, Any],
) -> List[Dict[str, Any]]:
    context_str = json.dumps(context, indent=2)
    system = f"{CHAT_SYSTEM_PROMPT}\n\n### Current User Context:\n{context_str}\n"
    llm_messages = [{"role": "system", "content": system}]
    for m in messages[-10:]:
        role = m.get("role", "user")
        content = m.get("content", "")
        image = m.get("image")
        if role == "user" and image:
            llm_messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": content or "Please inspect and analyze this image:"},
                    {"type": "image_url", "image_url": {"url": image}},
                ],
            })
        else:
            llm_messages.append({"role": role, "content": content})
    return llm_messages


async def process_chat_message(
    messages: List[Dict[str, Any]],
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    client_info = get_client()
    context = context or {}
    last_user_query = ""

    for m in reversed(messages):
        if m.get("role") == "user":
            raw = m.get("content", "")
            last_user_query = raw if isinstance(raw, str) else ""
            break

    # GitHub URL enrichment
    if "github.com/" in last_user_query:
        import asyncio
        github_info = await asyncio.to_thread(_fetch_github_repo_summary, last_user_query)
        if github_info:
            context["githubInspection"] = github_info

    if client_info is None:
        return _smart_fallback_response(last_user_query, context)

    llm_messages = _build_llm_messages(messages, context)
    collected_actions: List[Dict[str, Any]] = []

    try:
        # Agent loop — up to 5 iterations of tool calling
        for _iteration in range(5):
            try:
                response = await client_info["client"].chat.completions.create(
                    model=client_info["model"],
                    temperature=0.4,
                    messages=llm_messages,
                    tools=AGENT_TOOLS,
                    tool_choice="auto",
                )
            except Exception:
                # Model may not support tools param — fall back to no-tools call
                response = await client_info["client"].chat.completions.create(
                    model=client_info["model"],
                    temperature=0.4,
                    messages=llm_messages,
                )

            choice = response.choices[0]
            msg = choice.message

            # If the model made tool calls, collect them and feed results back
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                llm_messages.append(msg)
                for tc in msg.tool_calls:
                    args = json.loads(tc.function.arguments) if isinstance(tc.function.arguments, str) else tc.function.arguments
                    action = _tool_call_to_action(tc.function.name, args)
                    collected_actions.append(action)
                    llm_messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps({"status": "queued", "action": action["type"], "details": action["data"]}),
                    })
                continue

            # Text response — we're done
            content = msg.content or ""

            # Try parsing as the old JSON format for backward compat with prompt-based models
            parsed = parse_llm_json(content)
            if isinstance(parsed, dict) and "reply" in parsed:
                old_actions = parsed.get("actions", [])
                if isinstance(old_actions, list):
                    collected_actions.extend(old_actions)
                return {
                    "reply": parsed["reply"],
                    "actions": collected_actions,
                    "suggestedFollowUps": parsed.get("suggestedFollowUps", []),
                }

            return {
                "reply": content.strip() or "Here's what I found for you!",
                "actions": collected_actions,
                "suggestedFollowUps": [
                    "Tell me more",
                    "Add this as a task",
                    "How do I practice this?",
                ],
            }

    except Exception as e:
        print(f"Chat agent error: {e}")

    return _smart_fallback_response(last_user_query, context)


async def auto_organize_tasks(
    tasks: List[Dict[str, Any]],
    hours_budget: int = 12,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Analyzes user's Kanban task board and reorganizes it into an optimal sprint schedule."""
    client_info = get_client()
    context = context or {}

    prompt = f"""You are the LevelUP AI Task & Kanban Auto-Scheduler.
Analyze the following list of user tasks across their Kanban board:
Tasks:
{json.dumps(tasks, indent=2)}

Learner Weekly Study Budget: {hours_budget} hours/week.

Your goal is to optimize their Kanban board:
1. Select 2 to 4 high-leverage tasks to move to 'IN_PROGRESS' (Today's / Current sprint) without exceeding daily capacity (~2-4 hours).
2. Ensure realistic priorities (HIGH, MEDIUM, LOW) based on deadlines and cognitive complexity.
3. Keep completed tasks in 'COMPLETED'.
4. Return a clear pedagogical rationale explaining why this schedule prevents burnout and maximizes learning velocity.

You MUST reply with a valid JSON object matching this schema:
{{
  "rationale": "Clear 2-sentence explanation of why these tasks were scheduled for today...",
  "moves": [
    {{
      "taskId": "id of task",
      "taskTitle": "task title",
      "targetStatus": "IN_PROGRESS" | "NOT_STARTED" | "COMPLETED",
      "priority": "HIGH" | "MEDIUM" | "LOW",
      "estimatedHours": number,
      "reason": "Short reason for this status/priority"
    }}
  ],
  "todaySprintHours": number,
  "suggestedNewTasks": [
    {{
      "title": "Optional new complementary task",
      "priority": "HIGH" | "MEDIUM",
      "estimatedHours": number
    }}
  ]
}}
"""

    if client_info is not None:
        try:
            response = await client_info['client'].chat.completions.create(
                model=client_info['model'],
                temperature=0.2,
                messages=[
                    {'role': 'system', 'content': 'You are a master productivity and learning scheduler. Always output valid JSON.'},
                    {'role': 'user', 'content': prompt}
                ]
            )
            content = response.choices[0].message.content or ''
            parsed = parse_llm_json(content)
            if isinstance(parsed, dict) and "moves" in parsed:
                return parsed
        except Exception as e:
            print(f"Auto-schedule LLM error: {e}")

    # Smart Fallback — respect hours_budget when scheduling focus tasks
    moves = []
    budgeted_hours = 0
    for idx, t in enumerate(tasks):
        t_id = t.get('id') or f"t_{idx}"
        status = t.get('status', 'NOT_STARTED')
        if status == 'COMPLETED':
            continue
        task_hours = 2  # estimated per task
        # Only promote to IN_PROGRESS while there is remaining budget
        if budgeted_hours + task_hours <= max(hours_budget, 0):
            moves.append({
                "taskId": t_id,
                "taskTitle": t.get('title', 'Task'),
                "targetStatus": "IN_PROGRESS",
                "priority": "HIGH",
                "estimatedHours": task_hours,
                "reason": "Top priority focus for today's learning sprint"
            })
            budgeted_hours += task_hours
        else:
            moves.append({
                "taskId": t_id,
                "taskTitle": t.get('title', 'Task'),
                "targetStatus": "NOT_STARTED",
                "priority": "MEDIUM",
                "estimatedHours": task_hours,
                "reason": "Queued in backlog for upcoming sessions"
            })

    return {
        "rationale": f"Re-balanced your Kanban board based on your {hours_budget}h weekly budget. Scheduled {budgeted_hours}h of focus tasks for today's active sprint.",
        "moves": moves,
        "todaySprintHours": budgeted_hours,
        "suggestedNewTasks": []
    }


async def stream_chat_response(
    messages: List[Dict[str, Any]],
    context: Optional[Dict[str, Any]] = None,
):
    """Async generator yielding SSE events for streaming chat responses."""
    client_info = get_client()
    context = context or {}
    last_user_query = ""

    for m in reversed(messages):
        if m.get("role") == "user":
            raw = m.get("content", "")
            last_user_query = raw if isinstance(raw, str) else ""
            break

    if "github.com/" in last_user_query:
        import asyncio
        github_info = await asyncio.to_thread(_fetch_github_repo_summary, last_user_query)
        if github_info:
            context["githubInspection"] = github_info

    def _sse(data: Dict[str, Any]) -> str:
        return f"data: {json.dumps(data)}\n\n"

    if client_info is None:
        fallback = _smart_fallback_response(last_user_query, context)
        yield _sse({"type": "token", "content": fallback["reply"]})
        yield _sse({"type": "done", "actions": fallback["actions"], "suggestedFollowUps": fallback["suggestedFollowUps"]})
        return

    llm_messages = _build_llm_messages(messages, context)
    collected_actions: List[Dict[str, Any]] = []

    try:
        # Agent loop with streaming on the final text response
        for _iteration in range(5):
            # Non-streaming call for tool-calling iterations
            try:
                response = await client_info["client"].chat.completions.create(
                    model=client_info["model"],
                    temperature=0.4,
                    messages=llm_messages,
                    tools=AGENT_TOOLS,
                    tool_choice="auto",
                )
            except Exception:
                response = await client_info["client"].chat.completions.create(
                    model=client_info["model"],
                    temperature=0.4,
                    messages=llm_messages,
                )

            choice = response.choices[0]
            msg = choice.message

            if hasattr(msg, "tool_calls") and msg.tool_calls:
                llm_messages.append(msg)
                for tc in msg.tool_calls:
                    args = json.loads(tc.function.arguments) if isinstance(tc.function.arguments, str) else tc.function.arguments
                    action = _tool_call_to_action(tc.function.name, args)
                    collected_actions.append(action)
                    yield _sse({"type": "tool_call", "action": action})
                    llm_messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps({"status": "queued", "action": action["type"], "details": action["data"]}),
                    })
                continue

            # Final iteration — stream the text response
            try:
                stream = await client_info["client"].chat.completions.create(
                    model=client_info["model"],
                    temperature=0.4,
                    messages=llm_messages,
                    stream=True,
                )
                async for chunk in stream:
                    delta = chunk.choices[0].delta if chunk.choices else None
                    if delta and delta.content:
                        yield _sse({"type": "token", "content": delta.content})
            except Exception:
                # Streaming not supported — send the already-fetched content as one chunk
                content = msg.content or ""
                if content.strip():
                    yield _sse({"type": "token", "content": content})

            yield _sse({"type": "done", "actions": collected_actions, "suggestedFollowUps": ["Tell me more", "Add this as a task", "How do I practice this?"]})
            return

    except Exception as e:
        print(f"Stream chat error: {e}")
        fallback = _smart_fallback_response(last_user_query, context)
        yield _sse({"type": "token", "content": fallback["reply"]})
        yield _sse({"type": "done", "actions": fallback["actions"], "suggestedFollowUps": fallback["suggestedFollowUps"]})


ONBOARDING_SYSTEM_PROMPT = """You are the LevelUP onboarding agent. A new user just finished profile setup.

Based on their profile, use the provided tools to set up their workspace:
1. Create 3-5 skills they should track (based on their listed skills and career goal)
2. Create 1 task per skill — the first concrete learning step
3. Keep priorities realistic: 1-2 HIGH, rest MEDIUM

After calling the tools, write a short welcome message summarizing what you set up.
Be encouraging but concise — 3-4 sentences max."""


async def run_onboarding_agent(profile: Dict[str, Any]) -> Dict[str, Any]:
    client_info = get_client()
    if client_info is None:
        return _onboarding_fallback(profile)

    skills_str = profile.get("skills", "")
    if isinstance(skills_str, list):
        skills_str = ", ".join(skills_str)
    interests = profile.get("interests", "")
    if isinstance(interests, list):
        interests = ", ".join(interests)

    user_msg = json.dumps({
        "name": profile.get("name", ""),
        "education": profile.get("education", ""),
        "skills": skills_str,
        "interests": interests,
        "goals": profile.get("goals", ""),
        "experience": profile.get("experience", ""),
    })

    llm_messages = [
        {"role": "system", "content": ONBOARDING_SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ]
    collected_actions: List[Dict[str, Any]] = []

    try:
        for _iteration in range(5):
            try:
                response = await client_info["client"].chat.completions.create(
                    model=client_info["model"],
                    temperature=0.3,
                    messages=llm_messages,
                    tools=AGENT_TOOLS,
                    tool_choice="auto",
                )
            except Exception:
                response = await client_info["client"].chat.completions.create(
                    model=client_info["model"],
                    temperature=0.3,
                    messages=llm_messages,
                )

            choice = response.choices[0]
            msg = choice.message

            if hasattr(msg, "tool_calls") and msg.tool_calls:
                llm_messages.append(msg)
                for tc in msg.tool_calls:
                    args = json.loads(tc.function.arguments) if isinstance(tc.function.arguments, str) else tc.function.arguments
                    action = _tool_call_to_action(tc.function.name, args)
                    collected_actions.append(action)
                    llm_messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps({"status": "queued", "action": action["type"], "details": action["data"]}),
                    })
                continue

            content = msg.content or ""
            parsed = parse_llm_json(content)
            reply = parsed.get("reply", content) if isinstance(parsed, dict) else content

            return {
                "reply": reply.strip() or "Welcome to LevelUP! I've set up your workspace.",
                "actions": collected_actions,
            }

    except Exception as e:
        print(f"Onboarding agent error: {e}")

    return _onboarding_fallback(profile)


def _onboarding_fallback(profile: Dict[str, Any]) -> Dict[str, Any]:
    skills_raw = profile.get("skills", "")
    if isinstance(skills_raw, str):
        skill_list = [s.strip() for s in skills_raw.split(",") if s.strip()]
    else:
        skill_list = list(skills_raw) if skills_raw else []

    goal = profile.get("goals", "Software Engineer")
    actions = []

    for i, skill_name in enumerate(skill_list[:5]):
        actions.append({
            "type": "CREATE_SKILL",
            "data": {
                "title": skill_name,
                "categoryName": "From Profile",
                "priority": "HIGH" if i < 2 else "MEDIUM",
                "progress": 0,
            },
        })
        actions.append({
            "type": "CREATE_TASK",
            "data": {
                "title": f"Start learning {skill_name}: complete a beginner tutorial",
                "priority": "HIGH" if i < 2 else "MEDIUM",
                "status": "NOT_STARTED",
                "deadline": None,
                "notes": f"First step toward mastering {skill_name} for your {goal} goal.",
            },
        })

    return {
        "reply": f"Welcome to LevelUP! I've added {len(skill_list[:5])} skills from your profile and created a learning task for each. Head to your Dashboard to get started!",
        "actions": actions,
    }


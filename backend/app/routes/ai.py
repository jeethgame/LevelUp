from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Any, Dict, List, Optional

from app.services.ai_service import (
    generate_subskills,
    path_optimize,
    priority_suggestions,
    progress_insights,
    skill_gap,
    task_plan,
    time_estimate,
    weekly_report,
)
from app.services.chat_agent import process_chat_message, auto_organize_tasks, stream_chat_response, run_onboarding_agent
from app.utils.auth import get_optional_firebase_token

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix='/ai', tags=['AI'])


class GenerateSubskillsRequest(BaseModel):
    skillName: Optional[str] = ''
    courseLink: Optional[str] = ''


class ProgressInsightsRequest(BaseModel):
    skills: List[Dict[str, Any]] = Field(default_factory=list)
    tasks: List[Dict[str, Any]] = Field(default_factory=list)


class PrioritySuggestionsRequest(BaseModel):
    skills: List[Dict[str, Any]] = Field(default_factory=list)
    activityTimestamps: List[Dict[str, Any]] = Field(default_factory=list)


class TaskPlanRequest(BaseModel):
    availableTime: Optional[int] = 0
    tasks: List[Dict[str, Any]] = Field(default_factory=list)


class SkillGapRequest(BaseModel):
    targetRole: str
    skills: List[Dict[str, Any]] = Field(default_factory=list)


class PathOptimizeRequest(BaseModel):
    selectedSkills: List[Dict[str, Any]] = Field(default_factory=list)


class TimeEstimateRequest(BaseModel):
    skillName: str
    difficulty: Optional[str] = 'MEDIUM'


class WeeklyReportRequest(BaseModel):
    skills: List[Dict[str, Any]] = Field(default_factory=list)
    tasks: List[Dict[str, Any]] = Field(default_factory=list)


class ChatRequest(BaseModel):
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AutoOrganizeTasksRequest(BaseModel):
    tasks: List[Dict[str, Any]] = Field(default_factory=list)
    hoursBudget: Optional[int] = 12
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)


@router.post('/generate-subskills')
async def route_generate_subskills(body: GenerateSubskillsRequest, user_id: Optional[str] = Depends(get_optional_firebase_token)):
    result = await generate_subskills(body.dict())
    return {**result, 'userId': user_id or 'guest_user'}


@router.post('/progress-insights')
async def route_progress_insights(body: ProgressInsightsRequest, user_id: Optional[str] = Depends(get_optional_firebase_token)):
    result = await progress_insights(body.dict())
    return {**result, 'userId': user_id or 'guest_user'}


@router.post('/priority-suggestions')
async def route_priority_suggestions(body: PrioritySuggestionsRequest, user_id: Optional[str] = Depends(get_optional_firebase_token)):
    result = await priority_suggestions(body.dict())
    return {**result, 'userId': user_id or 'guest_user'}


@router.post('/task-plan')
async def route_task_plan(body: TaskPlanRequest, user_id: Optional[str] = Depends(get_optional_firebase_token)):
    result = await task_plan(body.dict())
    return {**result, 'userId': user_id or 'guest_user'}


@router.post('/skill-gap')
async def route_skill_gap(body: SkillGapRequest, user_id: Optional[str] = Depends(get_optional_firebase_token)):
    result = await skill_gap(body.dict())
    return {**result, 'userId': user_id or 'guest_user'}


@router.post('/path-optimize')
async def route_path_optimize(body: PathOptimizeRequest, user_id: Optional[str] = Depends(get_optional_firebase_token)):
    result = await path_optimize(body.dict())
    return {**result, 'userId': user_id or 'guest_user'}


@router.post('/time-estimate')
async def route_time_estimate(body: TimeEstimateRequest, user_id: Optional[str] = Depends(get_optional_firebase_token)):
    result = await time_estimate(body.dict())
    return {**result, 'userId': user_id or 'guest_user'}


@router.post('/weekly-report')
async def route_weekly_report(body: WeeklyReportRequest, user_id: Optional[str] = Depends(get_optional_firebase_token)):
    result = await weekly_report(body.dict())
    return {**result, 'userId': user_id or 'guest_user'}


@router.post('/chat')
@limiter.limit("20/minute")
async def route_chat(request: Request, body: ChatRequest, user_id: Optional[str] = Depends(get_optional_firebase_token)):
    result = await process_chat_message(body.messages, body.context)
    return {**result, 'userId': user_id or 'guest_user'}


@router.post('/chat/stream')
@limiter.limit("20/minute")
async def route_chat_stream(request: Request, body: ChatRequest, user_id: Optional[str] = Depends(get_optional_firebase_token)):
    return StreamingResponse(
        stream_chat_response(body.messages, body.context),
        media_type='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'},
    )


@router.post('/auto-organize-tasks')
@limiter.limit("10/minute")
async def route_auto_organize_tasks(request: Request, body: AutoOrganizeTasksRequest, user_id: Optional[str] = Depends(get_optional_firebase_token)):
    result = await auto_organize_tasks(body.tasks, body.hoursBudget, body.context)
    return {**result, 'userId': user_id or 'guest_user'}


class OnboardingRequest(BaseModel):
    name: Optional[str] = ''
    education: Optional[str] = ''
    skills: Optional[str] = ''
    interests: Optional[str] = ''
    goals: Optional[str] = ''
    experience: Optional[str] = ''


@router.post('/onboard')
@limiter.limit("5/minute")
async def route_onboard(request: Request, body: OnboardingRequest, user_id: Optional[str] = Depends(get_optional_firebase_token)):
    result = await run_onboarding_agent(body.dict())
    return {**result, 'userId': user_id or 'guest_user'}


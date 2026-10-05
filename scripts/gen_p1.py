import os

with open("backend/app/services/recommender_service.py", "w", encoding="utf-8") as f:
    f.write('''import os
import json
import uuid
import math
from typing import Any, Dict, List, Optional

try:
    from openai import AsyncAzureOpenAI, AsyncOpenAI
except Exception:
    AsyncAzureOpenAI = None
    AsyncOpenAI = None


def _get_ai_client():
    if AsyncAzureOpenAI is not None:
        key = os.getenv("AZURE_OPENAI_API_KEY")
        ep = os.getenv("AZURE_OPENAI_ENDPOINT")
        ver = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        if key and ep:
            return {
                "client": AsyncAzureOpenAI(api_key=key, azure_endpoint=ep, api_version=ver),
                "model": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")
            }
    if AsyncOpenAI is not None:
        key = os.getenv("OPENAI_API_KEY")
        if key:
            return {"client": AsyncOpenAI(api_key=key), "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini")}
    return None


CURATED_CATALOG = {
    "ai_ml": [
        {"title": "DeepLearning.AI: Prompt Engineering", "url": "https://www.deeplearning.ai/short-courses/", "type": "course", "provider": "DeepLearning.AI", "difficulty": "intermediate", "duration": "12 hours", "tags": ["python", "llm", "langchain", "ai"]},
        {"title": "Hugging Face Transformers", "url": "https://huggingface.co/learn", "type": "course", "provider": "Hugging Face", "difficulty": "advanced", "duration": "24 hours", "tags": ["transformers", "nlp", "pytorch", "ai"]},
        {"title": "Autonomous RAG Knowledge Engine", "url": "https://github.com/langchain-ai/rag-from-scratch", "type": "project", "provider": "GitHub Open Source", "difficulty": "intermediate", "duration": "15 hours", "tags": ["rag", "langchain", "python", "fastapi"]},
        {"title": "FastAPI Async Microservices", "url": "https://fastapi.tiangolo.com/tutorial/", "type": "docs", "provider": "Official Docs", "difficulty": "beginner", "duration": "8 hours", "tags": ["fastapi", "python", "asyncio"]},
    ],
    "fullstack": [
        {"title": "Full Stack Open: React & Node.js", "url": "https://fullstackopen.com/en/", "type": "course", "provider": "University of Helsinki", "difficulty": "intermediate", "duration": "40 hours", "tags": ["react", "node.js", "typescript"]},
        {"title": "Collaborative Canvas with WebSockets", "url": "https://github.com/fireship-io/fullstack-react-course", "type": "project", "provider": "GitHub Community", "difficulty": "intermediate", "duration": "16 hours", "tags": ["react", "websockets"]},
        {"title": "Modern TypeScript Handbook", "url": "https://www.typescriptlang.org/docs/", "type": "docs", "provider": "Microsoft", "difficulty": "beginner", "duration": "6 hours", "tags": ["typescript", "javascript"]},
    ],
    "backend_devops": [
        {"title": "Designing Data-Intensive Applications", "url": "https://dataintensive.net/", "type": "article", "provider": "O'Reilly", "difficulty": "advanced", "duration": "30 hours", "tags": ["distributed-systems", "database"]},
        {"title": "Docker & Kubernetes Cluster Guide", "url": "https://kubernetes.io/docs/tutorials/", "type": "docs", "provider": "CNCF", "difficulty": "intermediate", "duration": "18 hours", "tags": ["docker", "kubernetes", "devops"]},
        {"title": "High-Throughput Redis Cache Engine", "url": "https://github.com/karan/Projects", "type": "project", "provider": "Open Source Labs", "difficulty": "intermediate", "duration": "10 hours", "tags": ["caching", "redis", "postgres"]},
    ]
}
''')

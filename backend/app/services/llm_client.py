import json
import os
import re
from typing import Any, Dict, Optional

from dotenv import load_dotenv

load_dotenv(override=True)

try:
    from openai import AsyncAzureOpenAI, AsyncOpenAI
except Exception:
    AsyncAzureOpenAI = None
    AsyncOpenAI = None


def get_client() -> Optional[Dict[str, Any]]:
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("MINIMAX_API_KEY")
    if api_key in ("your-api-key-here", "mock-openai-key", ""):
        api_key = os.getenv("MINIMAX_API_KEY")

    base_url = (
        os.getenv("OPENAI_BASE_URL")
        or os.getenv("MINIMAX_BASE_URL")
        or "https://integrate.api.nvidia.com/v1"
    )
    model = (
        os.getenv("OPENAI_MODEL")
        or os.getenv("MINIMAX_MODEL")
        or "nvidia/nemotron-3.5-lightning-30b-a3b"
    )

    if api_key and AsyncOpenAI is not None:
        return {
            "client": AsyncOpenAI(api_key=api_key, base_url=base_url),
            "model": model,
        }

    if AsyncAzureOpenAI is not None:
        azure_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        if azure_key and endpoint and api_version:
            return {
                "client": AsyncAzureOpenAI(
                    api_key=azure_key,
                    azure_endpoint=endpoint,
                    api_version=api_version,
                ),
                "model": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini"),
            }

    return None


def parse_llm_json(content: str) -> Optional[Dict[str, Any]]:
    if not content:
        return None
    try:
        return json.loads(content)
    except Exception:
        pass
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass
    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(content[start : end + 1])
        except Exception:
            pass
    return None


async def ask_ai(
    system_prompt: str, payload: Dict[str, Any], fallback: Dict[str, Any]
) -> Dict[str, Any]:
    client_info = get_client()
    if client_info is None:
        return fallback

    try:
        response = await client_info["client"].chat.completions.create(
            model=client_info["model"],
            temperature=0.2,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(payload)},
            ],
        )
        content = response.choices[0].message.content or ""
        parsed = parse_llm_json(content)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        return fallback

    return fallback

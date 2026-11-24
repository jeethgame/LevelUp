import asyncio
import json
import logging
import os
import re
from functools import lru_cache
from typing import Any, Dict, Optional

from dotenv import load_dotenv

load_dotenv(override=True)

logger = logging.getLogger("levelup.llm")

try:
    from openai import AsyncAzureOpenAI, AsyncOpenAI
except Exception:
    AsyncAzureOpenAI = None
    AsyncOpenAI = None

MAX_RETRIES = 2
RETRY_BASE_DELAY = 1.0
REQUEST_TIMEOUT = 30.0


@lru_cache(maxsize=1)
def _build_client() -> Optional[Dict[str, Any]]:
    """Singleton — builds the client once and caches it."""
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
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=REQUEST_TIMEOUT,
            max_retries=0,
        )
        logger.info("LLM client initialized: %s @ %s", model, base_url)
        return {"client": client, "model": model}

    if AsyncAzureOpenAI is not None:
        azure_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        if azure_key and endpoint and api_version:
            client = AsyncAzureOpenAI(
                api_key=azure_key,
                azure_endpoint=endpoint,
                api_version=api_version,
                timeout=REQUEST_TIMEOUT,
                max_retries=0,
            )
            model = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")
            logger.info("LLM client initialized (Azure): %s", model)
            return {"client": client, "model": model}

    logger.warning("No LLM credentials configured — all AI calls will use fallbacks")
    return None


def get_client() -> Optional[Dict[str, Any]]:
    return _build_client()


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

    for attempt in range(MAX_RETRIES + 1):
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
            break
        except Exception as e:
            if attempt < MAX_RETRIES:
                delay = RETRY_BASE_DELAY * (2 ** attempt)
                logger.warning("LLM call attempt %d failed (%s), retrying in %.1fs", attempt + 1, e, delay)
                await asyncio.sleep(delay)
            else:
                logger.error("LLM call failed after %d attempts: %s", MAX_RETRIES + 1, e)

    return fallback

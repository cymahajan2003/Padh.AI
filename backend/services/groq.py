from typing import List

import httpx
from fastapi import HTTPException

from core.config import GROQ_API_KEY, GROQ_API_URL, GROQ_MODEL


async def groq_chat(
    messages: List[dict], temperature: float = 0.5, max_tokens: int = 2048
) -> str:
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured")

    async with httpx.AsyncClient(timeout=60.0, verify=False) as client:
        response = await client.post(
            GROQ_API_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}",
            },
            json={
                "model": GROQ_MODEL,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )

    if response.status_code != 200:
        error_body = (
            response.json()
            if response.headers.get("content-type", "").startswith("application/json")
            else {}
        )
        message = error_body.get("error", {}).get("message", response.text)
        raise HTTPException(
            status_code=response.status_code,
            detail=message or f"API error {response.status_code}",
        )

    data = response.json()
    content = (data.get("choices") or [{}])[0].get("message", {}).get("content") or ""
    return content.strip()

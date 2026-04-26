import os
from typing import List

import httpx
from fastapi import HTTPException

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"


async def groq_chat(
    messages: List[dict],
    temperature: float = 0.5,
    max_tokens: int = 2048,
) -> str:
    """Send a chat request to Groq and return the assistant reply as a string."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured")

    async with httpx.AsyncClient(timeout=60.0, verify=False) as client:
        r = await client.post(
            GROQ_API_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            json={
                "model": MODEL,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )

    if r.status_code != 200:
        err = (
            r.json()
            if r.headers.get("content-type", "").startswith("application/json")
            else {}
        )
        msg = err.get("error", {}).get("message", r.text) or f"API error {r.status_code}"
        raise HTTPException(status_code=r.status_code, detail=msg)

    data = r.json()
    content = (data.get("choices") or [{}])[0].get("message", {}).get("content") or ""
    return content.strip()

import asyncio

import httpx
from fastapi import HTTPException

from core.config import (
    BALANCE_ERROR_PHRASES,
    PLAG_CHECK_KEY,
    PLAGIARISM_API_URL,
    PLAGIARISM_MIN_TEXT_LEN,
)


async def plagiarism_check_org(text: str) -> float:
    if not PLAG_CHECK_KEY:
        raise HTTPException(
            status_code=500,
            detail="PLAG_CHECK API key not configured in .env",
        )

    if len(text) < PLAGIARISM_MIN_TEXT_LEN:
        text = text + " " * (PLAGIARISM_MIN_TEXT_LEN - len(text))

    headers = {"X-API-TOKEN": PLAG_CHECK_KEY}

    async with httpx.AsyncClient(timeout=120.0, verify=False) as client:
        post_response = await client.post(
            PLAGIARISM_API_URL,
            headers=headers,
            data={"language": "en", "text": text},
        )

        if post_response.status_code not in (200, 201):
            try:
                error_body = post_response.json()
                detail = error_body.get("message") or error_body.get("error") or post_response.text
            except Exception:
                detail = post_response.text or f"HTTP {post_response.status_code}"

            print(f"[PLAG DEBUG] POST status={post_response.status_code} detail={detail!r}")
            raise HTTPException(status_code=502, detail=f"Plagiarism API error: {detail}")

        body = post_response.json()
        if not body.get("success"):
            detail = body.get("message") or "Plagiarism API rejected the request"
            print(f"[PLAG DEBUG] API rejected: {detail!r}")
            raise HTTPException(status_code=502, detail=detail)

        text_id = ((body.get("data") or {}).get("text") or {}).get("id")
        if text_id is None:
            raise HTTPException(status_code=502, detail="Plagiarism API returned no text id")

        for attempt in range(90):
            if attempt > 0:
                await asyncio.sleep(2)

            status_response = await client.get(f"{PLAGIARISM_API_URL}/{text_id}", headers=headers)
            if status_response.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail=(
                        "Plagiarism status check failed: "
                        f"HTTP {status_response.status_code}"
                    ),
                )

            data = (status_response.json() or {}).get("data") or {}
            state = data.get("state")

            if state == 4:
                raise HTTPException(
                    status_code=502,
                    detail="Plagiarism check failed on the provider side",
                )

            if state == 5:
                percent_raw = (data.get("report") or {}).get("percent")
                if percent_raw is None:
                    raise HTTPException(
                        status_code=502,
                        detail="Plagiarism report missing percent",
                    )
                try:
                    return float(str(percent_raw).strip())
                except ValueError:
                    raise HTTPException(
                        status_code=502,
                        detail=f"Invalid plagiarism percent: {percent_raw!r}",
                    )

    raise HTTPException(
        status_code=504,
        detail="Plagiarism check timed out waiting for results",
    )


def is_balance_error(detail: str) -> bool:
    detail_lower = detail.lower()
    return any(phrase in detail_lower for phrase in BALANCE_ERROR_PHRASES)

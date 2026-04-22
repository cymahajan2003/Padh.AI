import asyncio
import os

import httpx
from fastapi import HTTPException

PLAGIARISM_API_URL = "https://plagiarismcheck.org/api/v1/text"
PLAGIARISM_THRESHOLD = 50
PLAGIARISM_MIN_TEXT_LEN = 80
PLAGIARISM_MAX_CHARS_FOR_CHECK = 1200
PLAGIARISM_FAIL_OPEN_ON_BALANCE_ERROR = True

BALANCE_ERROR_PHRASES = [
    "not enough pages",
    "insufficient balance",
    "insufficient pages",
    "no pages",
    "balance",
    "quota",
    "credits",
    "limit",
]


def is_balance_error(detail: str) -> bool:
    detail_lower = detail.lower()
    return any(phrase in detail_lower for phrase in BALANCE_ERROR_PHRASES)


async def check_plagiarism(text: str) -> float:
    """
    Submit text to plagiarismcheck.org, poll until checked,
    and return the plagiarism percentage (0–100).
    """
    plag_key = os.getenv("PLAG_CHECK")
    if not plag_key:
        raise HTTPException(
            status_code=500,
            detail="PLAG_CHECK API key not configured in .env",
        )

    if len(text) < PLAGIARISM_MIN_TEXT_LEN:
        text = text + " " * (PLAGIARISM_MIN_TEXT_LEN - len(text))

    headers = {"X-API-TOKEN": plag_key}

    async with httpx.AsyncClient(timeout=120.0, verify=False) as client:
        post_r = await client.post(
            PLAGIARISM_API_URL,
            headers=headers,
            data={"language": "en", "text": text},
        )

        if post_r.status_code not in (200, 201):
            try:
                err_body = post_r.json()
                detail = err_body.get("message") or err_body.get("error") or post_r.text
            except Exception:
                detail = post_r.text or f"HTTP {post_r.status_code}"
            print(f"[PLAG DEBUG] POST status={post_r.status_code} detail={detail!r}")
            raise HTTPException(status_code=502, detail=f"Plagiarism API error: {detail}")

        body = post_r.json()
        if not body.get("success"):
            detail = body.get("message") or "Plagiarism API rejected the request"
            print(f"[PLAG DEBUG] API rejected: {detail!r}")
            raise HTTPException(status_code=502, detail=detail)

        text_obj = (body.get("data") or {}).get("text") or {}
        text_id = text_obj.get("id")
        if text_id is None:
            raise HTTPException(status_code=502, detail="Plagiarism API returned no text id")

        # Poll until STATE_CHECKED (5) or STATE_FAILED (4)
        for attempt in range(90):
            if attempt > 0:
                await asyncio.sleep(2)

            get_r = await client.get(
                f"{PLAGIARISM_API_URL}/{text_id}",
                headers=headers,
            )
            if get_r.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail=f"Plagiarism status check failed: HTTP {get_r.status_code}",
                )

            data = (get_r.json() or {}).get("data") or {}
            state = data.get("state")

            if state == 4:
                raise HTTPException(
                    status_code=502,
                    detail="Plagiarism check failed on the provider side",
                )

            if state == 5:
                report = data.get("report") or {}
                percent_raw = report.get("percent")
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

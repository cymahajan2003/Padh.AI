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
    plag_key = os.getenv("PLAG_CHECK")

    if not plag_key:
        raise HTTPException(
            status_code=500,
            detail="PLAG_CHECK API key not configured in .env",
        )

    # 🔥 LIMIT TEXT (IMPORTANT)
    text = text[:PLAGIARISM_MAX_CHARS_FOR_CHECK]

    # 🔥 MIN LENGTH FIX
    if len(text) < PLAGIARISM_MIN_TEXT_LEN:
        text = text + " " * (PLAGIARISM_MIN_TEXT_LEN - len(text))

    headers = {"X-API-TOKEN": plag_key}

    async with httpx.AsyncClient(timeout=120.0) as client:

        # -------------------------
        # STEP 1: SUBMIT TEXT
        # -------------------------
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

            # ✅ HANDLE BALANCE ERROR GRACEFULLY
            if PLAGIARISM_FAIL_OPEN_ON_BALANCE_ERROR and is_balance_error(detail):
                print("[PLAG DEBUG] Skipping due to balance issue")
                return 0.0

            raise HTTPException(status_code=502, detail=f"Plagiarism API error: {detail}")

        body = post_r.json()

        if not body.get("success"):
            detail = body.get("message") or "Plagiarism API rejected the request"

            print(f"[PLAG DEBUG] API rejected: {detail!r}")

            if PLAGIARISM_FAIL_OPEN_ON_BALANCE_ERROR and is_balance_error(detail):
                print("[PLAG DEBUG] Skipping due to balance issue")
                return 0.0

            raise HTTPException(status_code=502, detail=detail)

        text_obj = (body.get("data") or {}).get("text") or {}
        text_id = text_obj.get("id")

        if text_id is None:
            raise HTTPException(status_code=502, detail="No text_id returned")

        # -------------------------
        # STEP 2: POLLING
        # -------------------------
        for attempt in range(60):  # ~2 minutes max
            if attempt > 0:
                await asyncio.sleep(2)

            get_r = await client.get(
                f"{PLAGIARISM_API_URL}/{text_id}",
                headers=headers,
            )

            if get_r.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail=f"Status check failed: HTTP {get_r.status_code}",
                )

            data = (get_r.json() or {}).get("data") or {}
            state = data.get("state")

            if state == 4:
                raise HTTPException(
                    status_code=502,
                    detail="Plagiarism check failed on provider side",
                )

            if state == 5:
                report = data.get("report") or {}
                percent_raw = report.get("percent")

                if percent_raw is None:
                    raise HTTPException(
                        status_code=502,
                        detail="Missing plagiarism percent",
                    )

                try:
                    score = float(str(percent_raw).strip())
                    print("[PLAG RESULT]", score)
                    return score
                except ValueError:
                    raise HTTPException(
                        status_code=502,
                        detail=f"Invalid percent: {percent_raw!r}",
                    )

    raise HTTPException(
        status_code=504,
        detail="Plagiarism check timeout",
    )
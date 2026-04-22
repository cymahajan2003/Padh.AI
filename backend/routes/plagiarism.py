from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.plagiarismService import (
    PLAGIARISM_FAIL_OPEN_ON_BALANCE_ERROR,
    PLAGIARISM_MAX_CHARS_FOR_CHECK,
    PLAGIARISM_THRESHOLD,
    check_plagiarism,
    is_balance_error,
)

router = APIRouter()


class PlagiarismCheckRequest(BaseModel):
    content: str


@router.post("")
async def plagiarism_check(req: PlagiarismCheckRequest):
    """Check text via plagiarismcheck.org; upload allowed if plagiarism < 50%."""
    content = (req.content or "").strip()
    if not content:
        return {
            "plagiarism_percentage": 0.0,
            "within_threshold": True,
            "threshold": PLAGIARISM_THRESHOLD,
            "message": "No content to check.",
        }

    text_for_api = content[:PLAGIARISM_MAX_CHARS_FOR_CHECK]

    try:
        percentage = await check_plagiarism(text_for_api)
    except HTTPException as e:
        detail = str(getattr(e, "detail", "") or "")
        print(f"[PLAG DEBUG] HTTPException detail={detail!r}")
        if PLAGIARISM_FAIL_OPEN_ON_BALANCE_ERROR and is_balance_error(detail):
            return {
                "plagiarism_percentage": 0.0,
                "within_threshold": True,
                "threshold": PLAGIARISM_THRESHOLD,
                "message": "Plagiarism check unavailable (provider balance insufficient). Document uploaded.",
            }
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Plagiarism check failed: {e}")

    percentage = max(0.0, min(100.0, percentage))
    return {
        "plagiarism_percentage": round(percentage, 2),
        "within_threshold": percentage < PLAGIARISM_THRESHOLD,
        "threshold": PLAGIARISM_THRESHOLD,
    }

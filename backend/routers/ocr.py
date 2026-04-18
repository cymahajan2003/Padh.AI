import io

import pytesseract
from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image

from core.config import ALLOWED_IMAGE_TYPES

router = APIRouter()


@router.post("/api/ocr")
async def ocr_extract_text(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}",
        )

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")
        text = pytesseract.image_to_string(image)
        return {"text": (text or "").strip()}
    except pytesseract.pytesseract.TesseractNotFoundError:
        raise HTTPException(
            status_code=503,
            detail=(
                "Tesseract OCR is not installed or not in PATH. "
                "Install it from https://github.com/UB-Mannheim/tesseract/wiki "
                "and set TESSERACT_CMD in backend .env to the path of tesseract.exe."
            ),
        )
    except (PermissionError, OSError) as exc:
        if getattr(exc, "winerror", None) == 5 or getattr(exc, "errno", None) == 13:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Access denied when running Tesseract. Try: "
                    "(1) Run the backend terminal as Administrator, or "
                    "(2) Install Tesseract to a folder outside Program Files "
                    "(e.g. C:\\Tesseract-OCR) and set TESSERACT_CMD in .env to that path."
                ),
            )
        raise HTTPException(status_code=500, detail=f"OCR failed: {exc}")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"OCR failed: {exc}")

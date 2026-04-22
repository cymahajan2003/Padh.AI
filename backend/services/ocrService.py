import io
import os

import pytesseract
from fastapi import HTTPException
from PIL import Image

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/bmp",
    "image/tiff",
}

# Optional: override Tesseract binary path via env (useful on Windows)
_tesseract_cmd = os.getenv("TESSERACT_CMD")
if _tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = _tesseract_cmd


def extract_text_from_image(file_bytes: bytes, content_type: str) -> str:
    """Run Tesseract OCR on raw image bytes and return extracted text."""
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{content_type}'. "
            f"Allowed: {', '.join(sorted(ALLOWED_IMAGE_TYPES))}",
        )

    try:
        image = Image.open(io.BytesIO(file_bytes))
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")
        text = pytesseract.image_to_string(image)
        return (text or "").strip()

    except pytesseract.pytesseract.TesseractNotFoundError:
        raise HTTPException(
            status_code=503,
            detail=(
                "Tesseract OCR is not installed or not in PATH. "
                "Install it from https://github.com/UB-Mannheim/tesseract/wiki "
                "and set TESSERACT_CMD in .env to the path of tesseract.exe."
            ),
        )
    except (PermissionError, OSError) as e:
        if getattr(e, "winerror", None) == 5 or getattr(e, "errno", None) == 13:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Access denied when running Tesseract. "
                    "Run the backend terminal as Administrator, or install Tesseract "
                    "outside Program Files and set TESSERACT_CMD in .env."
                ),
            )
        raise HTTPException(status_code=500, detail=f"OCR failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {e}")

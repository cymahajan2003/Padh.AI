from fastapi import APIRouter, File, UploadFile

from services.ocrService import ALLOWED_IMAGE_TYPES, extract_text_from_image

router = APIRouter()


@router.post("")
async def ocr_extract_text(file: UploadFile = File(...)):
    """Extract text from an uploaded image using Tesseract OCR."""
    file_bytes = await file.read()
    text = extract_text_from_image(file_bytes, file.content_type)
    return {"text": text}

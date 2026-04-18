import os

import pytesseract
from dotenv import load_dotenv

load_dotenv()

TESSERACT_CMD = os.getenv("TESSERACT_CMD")
if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

PLAGIARISM_API_URL = "https://plagiarismcheck.org/api/v1/text"
PLAG_CHECK_KEY = os.getenv("PLAG_CHECK")
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

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/bmp",
    "image/tiff",
}

ALLOWED_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

ALLOWED_CORS_ORIGIN_REGEX = r"http://(localhost|127\.0\.0\.1)(:\d+)?"

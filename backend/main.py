import asyncio
import io
import os
import json
import re
from typing import List, Optional
import httpx
import pytesseract
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image

load_dotenv()

# Optional: set Tesseract path (e.g. on Windows: C:\\Program Files\\Tesseract-OCR\\tesseract.exe)
_tesseract_cmd = os.getenv("TESSERACT_CMD")
if _tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = _tesseract_cmd

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "llama-3.3-70b-versatile"

PLAGIARISM_API_URL = "https://plagiarismcheck.org/api/v1/text"
PLAG_CHECK_KEY = os.getenv("PLAG_CHECK")
PLAGIARISM_THRESHOLD = 50
PLAGIARISM_MIN_TEXT_LEN = 80           # API requirement
PLAGIARISM_MAX_CHARS_FOR_CHECK = 1200  # ~1 page (~250 words); reduced to fit 1 remaining page
PLAGIARISM_FAIL_OPEN_ON_BALANCE_ERROR = True

# Phrases that indicate a quota/balance problem on the provider side
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

app = FastAPI(title="Padh.AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# ---------------------------------------------------------------------------
# Groq helper
# ---------------------------------------------------------------------------

async def groq_chat(messages: List[dict], temperature: float = 0.5, max_tokens: int = 2048) -> str:
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured")
    async with httpx.AsyncClient(timeout=60.0, verify=False) as client:
        r = await client.post(
            GROQ_API_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}",
            },
            json={
                "model": MODEL,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )
    if r.status_code != 200:
        err = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        msg = err.get("error", {}).get("message", r.text) or f"API error {r.status_code}"
        raise HTTPException(status_code=r.status_code, detail=msg)
    data = r.json()
    content = (data.get("choices") or [{}])[0].get("message", {}).get("content") or ""
    return content.strip()


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

class SummaryRequest(BaseModel):
    document_name: str
    content: str


@app.post("/api/summary")
async def summary(req: SummaryRequest):
    content = req.content
    if len(content) > 12000:
        content = content[:12000] + "\n\n[Content truncated for processing...]"

    system = """You are an expert document summarizer for a student learning platform called Padh.AI. Generate a well-structured, comprehensive summary of the provided document. Format your response using this exact structure:

## Summary
A 2-4 sentence summary of what the document is about.

## Key Points
- Point 1
- Point 2
- Point 3
(list all important points)

Keep the language clear, concise, and student-friendly. Do NOT include any other sections."""

    user = f'Please summarize the following document titled "{req.document_name}":\n\n{content}'
    summary_text = await groq_chat(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.3,
        max_tokens=2048,
    )
    return {"summary": summary_text}


# ---------------------------------------------------------------------------
# Plagiarism check (PlagiarismCheck.org API)
# ---------------------------------------------------------------------------

class PlagiarismCheckRequest(BaseModel):
    content: str


async def _plagiarism_check_org(text: str) -> float:
    """Submit text to plagiarismcheck.org, poll until checked, return plagiarism percent (0–100)."""
    if not PLAG_CHECK_KEY:
        raise HTTPException(
            status_code=500,
            detail="PLAG_CHECK API key not configured in .env",
        )

    # API requires at least 80 characters
    if len(text) < PLAGIARISM_MIN_TEXT_LEN:
        text = text + " " * (PLAGIARISM_MIN_TEXT_LEN - len(text))

    headers = {"X-API-TOKEN": PLAG_CHECK_KEY}

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

            # Debug: print exact error so you can see it in the backend terminal
            print(f"[PLAG DEBUG] POST status={post_r.status_code} detail={detail!r}")

            raise HTTPException(
                status_code=502,
                detail=f"Plagiarism API error: {detail}",
            )

        body = post_r.json()
        if not body.get("success"):
            detail = body.get("message") or "Plagiarism API rejected the request"
            # Debug: print exact rejection reason
            print(f"[PLAG DEBUG] API rejected: {detail!r}")
            raise HTTPException(status_code=502, detail=detail)

        text_obj = (body.get("data") or {}).get("text") or {}
        text_id = text_obj.get("id")
        if text_id is None:
            raise HTTPException(status_code=502, detail="Plagiarism API returned no text id")

        # Poll until STATE_CHECKED (5) or STATE_FAILED (4)
        for attempt in range(90):  # up to ~3 minutes at 2s between polls
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

            if state == 4:  # STATE_FAILED
                raise HTTPException(
                    status_code=502,
                    detail="Plagiarism check failed on the provider side",
                )

            if state == 5:  # STATE_CHECKED
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


def _is_balance_error(detail: str) -> bool:
    """Return True if the error detail string indicates a quota / balance problem."""
    detail_lower = detail.lower()
    return any(phrase in detail_lower for phrase in BALANCE_ERROR_PHRASES)


@app.post("/api/plagiarism-check")
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

    # Truncate to ~1 page so the single remaining provider page is not exceeded
    text_for_api = content[:PLAGIARISM_MAX_CHARS_FOR_CHECK]

    try:
        percentage = await _plagiarism_check_org(text_for_api)

    except HTTPException as e:
        detail = str(getattr(e, "detail", "") or "")
        print(f"[PLAG DEBUG] HTTPException detail={detail!r}")

        # If provider balance / quota is exhausted, fail open so upload still works
        if PLAGIARISM_FAIL_OPEN_ON_BALANCE_ERROR and _is_balance_error(detail):
            return {
                "plagiarism_percentage": 0.0,
                "within_threshold": True,
                "threshold": PLAGIARISM_THRESHOLD,
                "message": "Plagiarism check unavailable (provider balance insufficient). Document uploaded.",
            }
        raise

    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Plagiarism check failed: {str(e)}")

    percentage = max(0.0, min(100.0, percentage))
    within = percentage < PLAGIARISM_THRESHOLD
    return {
        "plagiarism_percentage": round(percentage, 2),
        "within_threshold": within,
        "threshold": PLAGIARISM_THRESHOLD,
    }


# ---------------------------------------------------------------------------
# OCR (Tesseract) for images and scanned documents
# ---------------------------------------------------------------------------

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp", "image/bmp", "image/tiff"}


@app.post("/api/ocr")
async def ocr_extract_text(file: UploadFile = File(...)):
    """Extract text from an uploaded image or scanned document using Tesseract OCR."""
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
    except (PermissionError, OSError) as e:
        if getattr(e, "winerror", None) == 5 or getattr(e, "errno", None) == 13:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Access denied when running Tesseract. Try: "
                    "(1) Run the backend terminal as Administrator, or "
                    "(2) Install Tesseract to a folder outside Program Files "
                    "(e.g. C:\\Tesseract-OCR) and set TESSERACT_CMD in .env to that path."
                ),
            )
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")


# ---------------------------------------------------------------------------
# Quiz (with RAG for document-based)
# ---------------------------------------------------------------------------

RAG_RETRIEVAL_SYSTEM = """You are a retrieval system for a student learning platform. Your task is to extract the most relevant sections from the given document that should be used to create quiz questions testing understanding of key concepts.

Rules:
- Return ONLY the extracted text from the document. Do not add any explanation, summary, or meta-commentary.
- Preserve the original order and wording of the document. Copy the most important passages that cover main concepts, definitions, and facts suitable for multiple-choice questions.
- Include diverse sections so quiz questions can cover different parts of the material.
- Limit the total output to about 3500 characters so it fits in the next step. If the document is long, select the most conceptually rich passages."""

QUIZ_SYSTEM = """You are a quiz generator for a student learning platform called Padh.AI. Generate exactly 5 multiple-choice questions based on the given topic or retrieved document content.

CRITICAL: You MUST respond with ONLY a valid JSON array, no markdown, no explanation, no code fences. The response must start with [ and end with ].

Each question object must have exactly this structure:
{"id":1,"question":"...","options":["A","B","C","D"],"correct":0}

Rules:
- "correct" is the 0-based index of the correct option (0, 1, 2, or 3)
- Each question must have exactly 4 options
- Questions should be educational, clear, and progressively challenging
- Cover different aspects of the topic or retrieved content
- Keep questions concise and student-friendly"""

_EMBEDDER_MODEL_NAME = "all-MiniLM-L6-v2"
_EMBEDDER = None


def _get_embedder():
    """Lazy-load sentence-transformers model for embeddings."""
    global _EMBEDDER
    if _EMBEDDER is None:
        from sentence_transformers import SentenceTransformer
        _EMBEDDER = SentenceTransformer(_EMBEDDER_MODEL_NAME)
    return _EMBEDDER


def _chunk_text(text: str, chunk_size: int = 900, overlap: int = 150, max_chunks: int = 80) -> List[str]:
    """Split long documents into overlapping chunks for classic embeddings-based retrieval."""
    text = (text or "").replace("\r\n", "\n").strip()
    if not text:
        return []
    chunks: List[str] = []
    start = 0
    n = len(text)
    while start < n and len(chunks) < max_chunks:
        end = min(n, start + chunk_size)
        # Prefer splitting on a nearby newline to keep chunks more coherent.
        if end < n:
            nl = text.rfind("\n", start, end)
            if nl != -1 and nl > start + int(chunk_size * 0.5):
                end = nl
        chunk = text[start:end].strip()
        if len(chunk) >= 120:
            chunks.append(chunk)
        if end >= n:
            break
        start = max(0, end - overlap)
    return chunks


async def retrieve_relevant_sections(content: str, document_name: str, max_chars: int = 12000) -> str:
    """Classic RAG retrieval: embeddings + FAISS to fetch relevant text chunks."""
    if not content or not content.strip():
        return ""
    # If content is short, skip vector search.
    if len(content) <= max_chars:
        return content
    chunks = _chunk_text(content, chunk_size=900, overlap=150, max_chunks=80)
    if not chunks:
        return content[:max_chars]

    import numpy as np
    import faiss

    embedder = _get_embedder()
    # Normalize vectors so inner product == cosine similarity.
    chunk_vecs = embedder.encode(chunks, convert_to_numpy=True, normalize_embeddings=True)
    chunk_vecs = np.asarray(chunk_vecs, dtype="float32")
    dim = chunk_vecs.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(chunk_vecs)

    query = f"Key concepts and definitions for quiz questions from: {document_name}"
    q_vec = embedder.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    q_vec = np.asarray(q_vec, dtype="float32")
    top_k = min(8, len(chunks))
    _scores, idx = index.search(q_vec, top_k)
    selected_indices = sorted(set(idx[0].tolist()))
    context = "\n\n".join(chunks[i] for i in selected_indices)
    return context[:max_chars]


class QuizRequest(BaseModel):
    topic: Optional[str] = None
    document_name: Optional[str] = None
    content: Optional[str] = None


@app.post("/api/quiz")
async def quiz(req: QuizRequest):
    if req.topic and req.topic.strip():
        # Topic-based: conceptual quiz from subject (no RAG)
        prompt = f'Generate 5 conceptual multiple-choice quiz questions about the topic: "{req.topic.strip()}". Make them educational, testing understanding of key concepts, and progressively challenging.'
        raw = await groq_chat(
            [{"role": "system", "content": QUIZ_SYSTEM}, {"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2048,
        )
    elif req.content and req.content.strip():
        # Document-based: RAG — retrieve relevant sections, then generate quiz
        name = req.document_name or "Document"
        content = req.content[:15000] if len(req.content) > 15000 else req.content
        retrieved = await retrieve_relevant_sections(content, name, max_chars=10000)
        context = retrieved[:6000] if len(retrieved) > 6000 else retrieved
        prompt = f'Generate 5 multiple-choice quiz questions based ONLY on the following retrieved sections from the document "{name}". Questions must be directly related to this material:\n\n{context}'
        raw = await groq_chat(
            [{"role": "system", "content": QUIZ_SYSTEM}, {"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2048,
        )
    else:
        raise HTTPException(status_code=400, detail="Provide either topic or content")

    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=502, detail=f"Invalid quiz response from AI: {e}")

    if not isinstance(parsed, list) or len(parsed) == 0:
        raise HTTPException(status_code=502, detail="Invalid quiz format received")

    questions = []
    for i, q in enumerate(parsed[:5]):
        questions.append({
            "id": q.get("id", i + 1),
            "question": q.get("question", ""),
            "options": q.get("options", []),
            "correct": int(q.get("correct", 0)) if isinstance(q.get("correct"), (int, float)) else 0,
        })
    return {"questions": questions}


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]


ASSISTANT_SYSTEM = (
    "You are Padh.AI, a smart and friendly learning assistant for students. "
    "Give short, direct, and to-the-point answers. Use 2-3 sentences max unless the user asks "
    "for a detailed explanation. Be clear, accurate, and student-friendly. "
    "Avoid unnecessary filler or pleasantries."
)


@app.post("/api/chat")
async def chat(req: ChatRequest):
    if not req.messages:
        raise HTTPException(status_code=400, detail="messages required")
    api_messages = [{"role": "system", "content": ASSISTANT_SYSTEM}]
    for m in req.messages:
        api_messages.append({"role": m.role, "content": m.content})
    reply = await groq_chat(api_messages, temperature=0.5, max_tokens=512)
    return {"message": reply}


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok"}
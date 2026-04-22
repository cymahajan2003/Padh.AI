import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import chat, ocr, plagiarism, summary
from routes import quiz
from routes.conceptualRoutes import router as conceptual_router

load_dotenv()

app = FastAPI(title="Padh.AI API")

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
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
# Routers
# ---------------------------------------------------------------------------
app.include_router(conceptual_router,  prefix="/api")                    # /api/generate, /api/evaluate …
app.include_router(quiz.router,        prefix="/api/quiz")               # /api/quiz/generate, /submit, /generate-more
app.include_router(summary.router,     prefix="/api/summary")            # /api/summary
app.include_router(plagiarism.router,  prefix="/api/plagiarism-check")   # /api/plagiarism-check
app.include_router(ocr.router,         prefix="/api/ocr")                # /api/ocr
app.include_router(chat.router,        prefix="/api/chat")               # /api/chat

# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

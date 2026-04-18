from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import ALLOWED_CORS_ORIGIN_REGEX, ALLOWED_CORS_ORIGINS
from routers.chat import router as chat_router
from routers.health import router as health_router
from routers.ocr import router as ocr_router
from routers.plagiarism import router as plagiarism_router
from routers.quiz import router as quiz_router
from routers.summary import router as summary_router


def create_app() -> FastAPI:
    app = FastAPI(title="Padh.AI API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_CORS_ORIGINS,
        allow_origin_regex=ALLOWED_CORS_ORIGIN_REGEX,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    app.include_router(summary_router)
    app.include_router(plagiarism_router)
    app.include_router(ocr_router)
    app.include_router(quiz_router)
    app.include_router(chat_router)
    app.include_router(health_router)
    return app

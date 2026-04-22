from fastapi import APIRouter
from pydantic import BaseModel

from services.summaryService import summarize_document

router = APIRouter()


class SummaryRequest(BaseModel):
    document_name: str
    content: str


@router.post("")
async def summary(req: SummaryRequest):
    summary_text = await summarize_document(req.document_name, req.content)
    return {"summary": summary_text}

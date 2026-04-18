from fastapi import APIRouter

from schemas.summary import SummaryRequest
from services.groq import groq_chat

router = APIRouter()


SUMMARY_SYSTEM_PROMPT = """You are an expert document summarizer for a student learning platform called Padh.AI. Generate a well-structured, comprehensive summary of the provided document. Format your response using this exact structure:

## Summary
A 2-4 sentence summary of what the document is about.

## Key Points
- Point 1
- Point 2
- Point 3
(list all important points)

Keep the language clear, concise, and student-friendly. Do NOT include any other sections."""


@router.post("/api/summary")
async def summary(req: SummaryRequest):
    content = req.content
    if len(content) > 12000:
        content = content[:12000] + "\n\n[Content truncated for processing...]"

    user_prompt = (
        f'Please summarize the following document titled "{req.document_name}":\n\n{content}'
    )
    summary_text = await groq_chat(
        [
            {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=2048,
    )
    return {"summary": summary_text}

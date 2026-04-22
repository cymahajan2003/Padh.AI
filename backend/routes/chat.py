from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.chatService import socratic_chat

router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]


@router.post("")
async def chat(req: ChatRequest):
    if not req.messages:
        raise HTTPException(status_code=400, detail="messages required")

    messages = [{"role": m.role, "content": m.content} for m in req.messages]
    reply = await socratic_chat(messages)
    return {"message": reply}

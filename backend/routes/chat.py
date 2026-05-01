from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.chatService import socratic_chat
from services.supabaseClient import supabase_admin

router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    document_id: Optional[str] = None   # 🔥 NEW


@router.post("")
async def chat(req: ChatRequest):
    if not req.messages:
        raise HTTPException(status_code=400, detail="messages required")

    try:
        # -------------------------------
        # 1. BASE CHAT MESSAGES
        # -------------------------------
        messages = [
            {"role": m.role, "content": m.content}
            for m in req.messages
        ]

        # -------------------------------
        # 2. DOCUMENT CONTEXT (IF EXISTS)
        # -------------------------------
        if req.document_id:
            doc_res = supabase_admin.table("documents") \
                .select("content, file_name") \
                .eq("id", req.document_id) \
                .single() \
                .execute()

            doc = doc_res.data

            if doc and doc.get("content"):
                # 🔥 limit to avoid token overflow
                context = doc["content"][:4000]

                messages.append({
                    "role": "system",
                    "content": (
                        f"You are answering based on the document: {doc.get('file_name')}\n\n"
                        f"Document content:\n{context}"
                    )
                })

        # -------------------------------
        # 3. RUN SOCrATIC CHAT
        # -------------------------------
        reply = await socratic_chat(messages)

        return {"message": reply}

    except Exception as e:
        print("[CHAT ERROR]", e)
        raise HTTPException(status_code=500, detail=str(e))
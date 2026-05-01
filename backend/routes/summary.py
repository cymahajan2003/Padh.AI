from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.summaryService import summarize_document
from services.supabaseClient import supabase_admin

router = APIRouter()


# -------------------------------
# Request Model
# -------------------------------
class SummaryRequest(BaseModel):
    document_id: str


# -------------------------------
# Summary Route
# -------------------------------
@router.post("/")
async def summary(req: SummaryRequest):
    try:
        # -------------------------------
        # 1. FETCH DOCUMENT FROM DB
        # -------------------------------
        res = supabase_admin.table("documents") \
            .select("*") \
            .eq("id", req.document_id) \
            .single() \
            .execute()

        doc = res.data

        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        # -------------------------------
        # 2. GET STORED CONTENT
        # -------------------------------
        content = doc.get("content")

        if not content or not content.strip():
            raise HTTPException(status_code=400, detail="Document content is empty")

        # -------------------------------
        # 3. GENERATE SUMMARY
        # -------------------------------
        summary_text = await summarize_document(
            doc.get("file_name", "Document"),
            content
        )

        # -------------------------------
        # 4. RETURN RESPONSE
        # -------------------------------
        return {
            "summary": summary_text
        }

    except HTTPException:
        raise

    except Exception as e:
        print("[SUMMARY ERROR]:", e)
        raise HTTPException(status_code=500, detail=str(e))
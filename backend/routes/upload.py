from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from services.supabaseClient import supabase_admin
from services.plagiarismService import (
    check_plagiarism,
    PLAGIARISM_THRESHOLD,
    PLAGIARISM_MAX_CHARS_FOR_CHECK,
    PLAGIARISM_FAIL_OPEN_ON_BALANCE_ERROR,
    is_balance_error
)
from services.ocrService import extract_text_from_image
from utils.auth import get_current_user

from PyPDF2 import PdfReader
import io

router = APIRouter()


@router.post("/")
async def upload_file(file: UploadFile = File(...), user=Depends(get_current_user)):
    try:
        print("USER:", user.id)

        # -------------------------------
        # 1. READ FILE
        # -------------------------------
        file_bytes = await file.read()

        # -------------------------------
        # 2. EXTRACT TEXT (PDF + OCR + IMAGE)
        # -------------------------------
        text_content = ""

        # ✅ PDF handling
        if file.filename.lower().endswith(".pdf"):
            try:
                reader = PdfReader(io.BytesIO(file_bytes))

                for page in reader.pages:
                    text_content += page.extract_text() or ""

                # 🔥 OCR fallback if PDF has no extractable text
                if not text_content.strip():
                    print("[OCR FALLBACK] Using OCR for scanned PDF")
                    text_content = extract_text_from_image(file_bytes, "application/pdf")

            except Exception as e:
                print("[PDF ERROR]", e)
                text_content = ""

        # ✅ IMAGE handling (direct OCR)
        elif file.content_type and file.content_type.startswith("image/"):
            print("[OCR] Processing image file")
            text_content = extract_text_from_image(file_bytes, file.content_type)

        # ✅ OTHER FILES (txt, etc.)
        else:
            try:
                text_content = file_bytes.decode(errors="ignore")
            except Exception as e:
                print("[DECODE ERROR]", e)
                text_content = ""

        # -------------------------------
        # 3. HANDLE EMPTY TEXT
        # -------------------------------
        if not text_content.strip():
            print("[PLAG DEBUG] No text extracted, skipping plagiarism")
            plagiarism_score = 0.0
            full_text = ""
        else:
            # 🔥 KEEP FULL TEXT FOR STORAGE
            full_text = text_content

            # 🔥 USE LIMITED TEXT FOR PLAG CHECK
            plag_text = text_content[:PLAGIARISM_MAX_CHARS_FOR_CHECK]

            # -------------------------------
            # 4. PLAGIARISM CHECK
            # -------------------------------
            try:
                plagiarism_score = await check_plagiarism(plag_text)
            except HTTPException as e:
                detail = str(e.detail).lower()
                print("[PLAG ERROR]", detail)

                if PLAGIARISM_FAIL_OPEN_ON_BALANCE_ERROR and is_balance_error(detail):
                    print("[PLAG] Skipping due to balance issue")
                    plagiarism_score = 0.0
                else:
                    raise

        print(f"[PLAG RESULT] {plagiarism_score}")

        # -------------------------------
        # 5. BLOCK HIGH PLAGIARISM
        # -------------------------------
        if plagiarism_score >= PLAGIARISM_THRESHOLD:
            raise HTTPException(status_code=400, detail="High plagiarism detected")

        # -------------------------------
        # 6. UPLOAD TO STORAGE
        # -------------------------------
        file_path = f"{user.id}/{file.filename}"

        upload_res = supabase_admin.storage.from_("documents").upload(
            file_path, file_bytes
        )

        if hasattr(upload_res, "error") and upload_res.error:
            raise HTTPException(status_code=500, detail=str(upload_res.error))

        # -------------------------------
        # 7. GET PUBLIC URL
        # -------------------------------
        public_url = supabase_admin.storage.from_("documents").get_public_url(file_path)

        # -------------------------------
        # 8. SAVE TO DATABASE (IMPORTANT)
        # -------------------------------
        db_res = supabase_admin.table("documents").insert({
            "user_id": user.id,
            "file_name": file.filename,
            "file_url": public_url,
            "plagiarism_score": plagiarism_score,
            "content": full_text   # 🔥 STORED FOR SUMMARY / QUIZ / RAG
        }).execute()

        print("DB RESPONSE:", db_res.data)

        # -------------------------------
        # 9. RETURN RESPONSE (WITH ID)
        # -------------------------------
        return {
            "message": "Low plagiarism. Document successfully uploaded.",
            "file_url": public_url,
            "plagiarism_score": plagiarism_score,
            "id": db_res.data[0]["id"]   # 🔥 REQUIRED FOR FRONTEND
        }

    except HTTPException:
        raise
    except Exception as e:
        print("UPLOAD ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))
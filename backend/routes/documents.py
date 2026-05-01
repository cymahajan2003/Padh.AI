from fastapi import APIRouter, Depends
from services.supabaseClient import supabase_admin
from utils.auth import get_current_user

router = APIRouter()

@router.get("/")
def get_documents(user=Depends(get_current_user)):
    try:
        res = supabase_admin.table("documents") \
            .select("*") \
            .eq("user_id", user.id) \
            .order("created_at", desc=True) \
            .execute()

        return res.data or []

    except Exception as e:
        return []
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.supabaseClient import supabase_auth

router = APIRouter()

class AuthRequest(BaseModel):
    email: str
    password: str

# ---------------- SIGNUP ----------------
@router.post("/signup")
def signup(data: AuthRequest):
    res = supabase_auth.auth.sign_up({
        "email": data.email,
        "password": data.password
    })

    if res.user is None:
        raise HTTPException(status_code=400, detail="Signup failed")

    return {
        "message": "Signup successful",
        "user_id": res.user.id
    }

# ---------------- LOGIN ----------------
@router.post("/login")
def login(data: AuthRequest):
    res = supabase_auth.auth.sign_in_with_password({
        "email": data.email,
        "password": data.password
    })

    if res.user is None:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return {
        "message": "Login successful",
        "access_token": res.session.access_token,
        "user_id": res.user.id
    }
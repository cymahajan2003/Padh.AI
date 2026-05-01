from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

security = HTTPBearer()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    try:
        user = supabase.auth.get_user(token)

        if not user or not user.user:
            raise HTTPException(status_code=401, detail="Invalid token")

        return user.user

    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized")
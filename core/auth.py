from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from db.supabase import supabase

security = HTTPBearer(auto_error=False)  # ← add auto_error=False

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = credentials.credentials
    try:
        res = supabase.auth.get_user(token)
        if not res or not res.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return res.user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {str(e)}")

def get_admin_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    user = get_current_user(credentials)
    try:
        profile = supabase.table("users").select("role").eq("id", user.id).single().execute()
        if not profile.data or profile.data["role"] != "admin":
            raise HTTPException(status_code=403, detail="Access denied — admin only")
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
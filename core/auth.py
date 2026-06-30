from fastapi import HTTPException, Header
from db.supabase import supabase

def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    # Handle both "Bearer token" and just "token"
    if authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
    else:
        token = authorization
    
    try:
        res = supabase.auth.get_user(token)
        if not res or not res.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return res.user
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {str(e)}")

def get_admin_user(authorization: str = Header(None)):
    user = get_current_user(authorization)
    
    try:
        profile = supabase.table("users").select("role").eq("id", user.id).single().execute()
        
        if not profile.data or profile.data["role"] != "admin":
            raise HTTPException(status_code=403, detail="Access denied — admin only")
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from db.supabase import supabase
import os
from dotenv import load_dotenv

load_dotenv()

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        
        # Get user from Supabase
        response = supabase.auth.get_user(token)
        
        if not response or not response.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = response.user
        
        # Return a dictionary
        return {
            "id": user.id,
            "email": user.email,
            "role": user.user_metadata.get("role", "homeowner"),
            "full_name": user.user_metadata.get("full_name", ""),
            "phone_number": user.user_metadata.get("phone_number", "")
        }
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

def get_admin_user(current_user: dict = Depends(get_current_user)):
    """Check if user is admin"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied — admin only")
    return current_user

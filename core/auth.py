from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from db.supabase import supabase

security = HTTPBearer(auto_error=False)

class UserObj:
    """Supports both current_user.id and current_user['id']"""
    def __init__(self, data: dict):
        self._data = data
        self.id = data.get("id")
        self.email = data.get("email")
        self.role = data.get("role")
        self.full_name = data.get("full_name")
        self.phone_number = data.get("phone_number")

    def get(self, key, default=None):
        return self._data.get(key, default)

    def __getitem__(self, key):
        return self._data[key]

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        if not credentials:
            raise HTTPException(status_code=401, detail="Missing token")
        token = credentials.credentials
        response = supabase.auth.get_user(token)
        if not response or not response.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = response.user
        db_role = user.user_metadata.get("role", "homeowner")
        mapped_role = "architect" if db_role == "contractor" else db_role
        return UserObj({
            "id": user.id,
            "email": user.email,
            "role": mapped_role,
            "full_name": user.user_metadata.get("full_name", ""),
            "phone_number": user.user_metadata.get("phone_number", "")
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

def get_admin_user(current_user = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied — admin only")
    return current_user
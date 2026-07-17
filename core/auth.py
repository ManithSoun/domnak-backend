from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from db.supabase import supabase
import logging

logger = logging.getLogger("domnak")

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
            logger.warning("Auth failed: Missing credentials")
            raise HTTPException(status_code=401, detail="Missing token")
        token = credentials.credentials
        if not token:
            logger.warning("Auth failed: Empty token")
            raise HTTPException(status_code=401, detail="Missing token")
        logger.info(f"Validating token: {token[:30]}...")
        
        # Retry logic for transient connection errors with exponential backoff
        user = None
        last_error = None
        for attempt in range(5):  # Increased from 3 to 5 attempts
            try:
                response = supabase.auth.get_user(token)
                if response and response.user:
                    user = response.user
                    break
            except Exception as e:
                last_error = e
                error_str = str(e)
                # Only retry on transient errors, not on invalid token
                if "invalid" in error_str.lower() or "malformed" in error_str.lower():
                    # Don't retry for invalid tokens
                    break
                if attempt < 4:  # 5 total attempts
                    import time
                    time.sleep(0.3 * (attempt + 1))  # Exponential backoff: 0.3, 0.6, 0.9, 1.2s
        
        if not user:
            logger.warning(f"Auth failed: Could not validate token - {last_error}")
            raise HTTPException(status_code=401, detail="Invalid token")
        
        logger.info(f"User authenticated: {user.id}")
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
        logger.error(f"Auth error: {e}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

def get_admin_user(current_user = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied — admin only")
    return current_user
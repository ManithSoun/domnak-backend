from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from db.supabase import supabase

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        
        # Use Supabase to validate the token
        response = supabase.auth.get_user(token)
        
        # Check if response is valid
        if not response:
            raise HTTPException(status_code=401, detail="Invalid token response")
        
        # Handle response as dictionary
        if isinstance(response, dict):
            user_data = response.get('user', {})
            if not user_data:
                raise HTTPException(status_code=401, detail="No user data in response")
            
            # Get user metadata
            metadata = user_data.get('user_metadata', {}) or {}
            
            return {
                "id": user_data.get('id'),
                "email": user_data.get('email'),
                "role": metadata.get("role", "homeowner"),
                "full_name": metadata.get("full_name", ""),
                "phone_number": metadata.get("phone_number", "")
            }
        else:
            # Handle as object (fallback)
            user = getattr(response, 'user', None)
            if not user:
                raise HTTPException(status_code=401, detail="No user in response")
            
            metadata = getattr(user, 'user_metadata', {}) or {}
            
            return {
                "id": getattr(user, 'id', None),
                "email": getattr(user, 'email', None),
                "role": metadata.get("role", "homeowner"),
                "full_name": metadata.get("full_name", ""),
                "phone_number": metadata.get("phone_number", "")
            }
        
    except Exception as e:
        print(f"Auth error: {str(e)}")
        print(f"Response type: {type(response) if 'response' in locals() else 'No response'}")
        if 'response' in locals():
            print(f"Response: {response}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

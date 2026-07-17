from fastapi import APIRouter, HTTPException
from models.auth import SignupRequest, LoginRequest
from db.supabase import supabase

router = APIRouter()

@router.post("/signup")
def signup(data: SignupRequest):
    try:
        # Map 'architect' to 'contractor' for DB/trigger enum compatibility
        db_role = "contractor" if data.role == "architect" else data.role
        
        # Step 1 - create auth user
        res = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password,
            "options": {
              "data": {
                "full_name": data.full_name,
                "role": db_role,
                "phone_number": data.phone_number
              }
            }
        })

        if res.user is None:
            raise HTTPException(status_code=400, detail="Signup failed")

        # Step 2 - Create user record in users table
        supabase.table("users").upsert({
            "id": res.user.id,
            "email": data.email,
            "full_name": data.full_name,
            "role": db_role,
            "phone_number": data.phone_number or ""
        }).execute()

        return {"message": "Signup successful", "user_id": res.user.id}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
      
@router.post("/login")
def login(data: LoginRequest):
  try:
    res = supabase.auth.sign_in_with_password({
      "email": data.email,
      "password": data.password
    })
    
    # Ensure user record exists (create if not)
    existing = supabase.table("users").select("role, full_name").eq("id", res.user.id).execute()
    
    if not existing.data:
        supabase.table("users").upsert({
            "id": res.user.id,
            "email": data.email,
            "full_name": res.user.user_metadata.get("full_name", ""),
            "role": res.user.user_metadata.get("role", "homeowner"),
            "phone_number": res.user.user_metadata.get("phone_number", "")
        }).execute()
        profile = supabase.table("users").select("role, full_name").eq("id", res.user.id).execute()
    else:
        profile = existing
    
    profile_data = profile.data[0] if profile.data else {"role": "homeowner", "full_name": ""}
    db_role = profile_data["role"]
    mapped_role = "architect" if db_role == "contractor" else db_role
    return {
      "access_token": res.session.access_token,
      "user_id": res.user.id,
      "role": mapped_role,
      "full_name": profile_data["full_name"]
    }

  except Exception as e:
    raise HTTPException(status_code=401, detail=str(e))
  

@router.get("/me")
def get_me(user_id: str):
  try:
    # First try to get existing record
    res = supabase.table("users").select("*").eq("id", user_id).execute()
    
    # If no record exists, create one from auth metadata
    if not res.data:
        print(f"[GET_ME] No users record for {user_id}, creating...")
        user = supabase.auth.get_user(user_id)
        if user.user:
            supabase.table("users").upsert({
                "id": user.user.id,
                "email": user.user.email,
                "full_name": user.user.user_metadata.get("full_name", ""),
                "role": user.user.user_metadata.get("role", "homeowner"),
                "phone_number": user.user.user_metadata.get("phone_number", "")
            }).execute()
            res = supabase.table("users").select("*").eq("id", user_id).execute()
    
    if res.data:
      db_role = res.data[0].get("role")
      result = res.data[0].copy()
      result["role"] = "architect" if db_role == "contractor" else db_role
      return result
    return None
  except Exception as e:
    raise HTTPException(status_code=404, detail=str(e))

@router.get("/users")
def list_users():
    try:
        res = supabase.table("users").select("id, full_name, role").execute()
        users = res.data or []
        for u in users:
            if u.get("role") == "contractor":
                u["role"] = "architect"
        return {"data": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/me")
def update_me(user_id: str, data: dict):
    try:
        # Only allow updating full_name (the only writable field we know exists)
        allowed_fields = {"full_name"}
        filtered_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not filtered_data:
            return {"message": "No valid fields to update"}
        
        res = supabase.table("users").update(filtered_data).eq("id", user_id).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

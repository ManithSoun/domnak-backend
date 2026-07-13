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
    profile = supabase.table("users").select("role, full_name").eq("id", res.user.id).single().execute()
    db_role = profile.data["role"]
    mapped_role = "architect" if db_role == "contractor" else db_role
    return {
      "access_token": res.session.access_token,
      "user_id": res.user.id,
      "role": mapped_role,
      "full_name": profile.data["full_name"]
    }


  except Exception as e:
    raise HTTPException(status_code=401, detail=str(e))
  

@router.get("/me")
def get_me(user_id: str):
  try:
    res = supabase.table("users").select("*").eq("id", user_id).single().execute()
    if res.data:
      db_role = res.data.get("role")
      res.data["role"] = "architect" if db_role == "contractor" else db_role
    return res.data
  except Exception as e:
    raise HTTPException(status_code=404, detail=str(e))

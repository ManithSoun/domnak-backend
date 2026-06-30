from fastapi import APIRouter, HTTPException
from models.auth import SignupRequest, LoginRequest
from db.supabase import supabase

router = APIRouter()

@router.post("/signup")
def signup(data: SignupRequest):
    try:
        # Step 1 - create auth user
        res = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password
        })

        if res.user is None:
            raise HTTPException(status_code=400, detail="Signup failed")

        # Step 2 - wait briefly then insert profile
        import time
        time.sleep(1)

        # Step 3 - insert into users table
        supabase.table("users").insert({
            "id": res.user.id,
            "full_name": data.full_name,
            "role": data.role,
            "phone_number": data.phone_number
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
    profile = supabase.table("users").select("role, full_name").eq("id", res.user.id).single().execute()
    return {
      "access_token": res.session.access_token,
      "user_id": res.user.id,
      "role": profile.data["role"],
      "full_name": profile.data["full_name"]
    }


  except Exception as e:
    raise HTTPException(status_code=401, detail=str(e))
  

@router.get("/me")
def get_me(user_id: str):
  try:
    res = supabase.table("users").select("*").eq("id", user_id).single().execute()
    return res.data
  except Exception as e:
    raise HTTPException(status_code=404, detail=str(e))

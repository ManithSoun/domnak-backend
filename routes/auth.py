from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from db.supabase import supabase
from utils.response import success, error
import os
from datetime import datetime, timedelta
import jwt

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    email: str
    password: str
    full_name: str
    phone_number: str
    role: str = "homeowner"

@router.post("/login")
def login(data: LoginRequest):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })
        
        if not response or not response.user:
            return error(message="Invalid credentials", status_code=401)
        
        return success(data={
            "access_token": response.session.access_token,
            "user_id": response.user.id,
            "role": response.user.user_metadata.get("role", "homeowner"),
            "full_name": response.user.user_metadata.get("full_name", "")
        })
    except Exception as e:
        return error(message=str(e), status_code=401)

@router.post("/signup")
def signup(data: SignupRequest):
    try:
        response = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password,
            "options": {
                "data": {
                    "full_name": data.full_name,
                    "phone_number": data.phone_number,
                    "role": data.role
                }
            }
        })
        
        if not response or not response.user:
            return error(message="Signup failed", status_code=400)
        
        return success(data={
            "id": response.user.id,
            "email": response.user.email,
            "full_name": data.full_name,
            "role": data.role
        })
    except Exception as e:
        return error(message=str(e), status_code=400)

@router.get("/me")
def get_me(user_id: str):
    try:
        response = supabase.table("users").select("*").eq("id", user_id).execute()
        if not response.data or len(response.data) == 0:
            return error(message="User not found", status_code=404)
        return success(data=response.data[0])
    except Exception as e:
        return error(message=str(e), status_code=500)

from fastapi import APIRouter, Depends, HTTPException
from models.chat import ChatRequest
from services.auth import get_current_user
from services.supabase import supabase 
import os
import json
from groq import Groq

router = APIRouter()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from core.auth import get_current_user
from utils.response import success, error
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    user_id: str

@router.post("/chat/stream")
def chat_stream(request: ChatRequest, current_user = Depends(get_current_user)):
    try:
        api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            return error(
                message="GROQ_API_KEY not found. Please add it to .env file",
                status_code=500
            )
        
        client = Groq(api_key=api_key)
        
        # Updated to current model
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": """You are a construction cost estimator expert for Cambodia. 
                    Help users with construction costs, materials, and building advice.
                    Provide practical, accurate information based on Cambodian market rates."""
                },
                {
                    "role": "user", 
                    "content": request.message
                }
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        response = completion.choices[0].message.content
        
        return success(data={
            "response": response,
            "user_id": request.user_id,
            "message": request.message,
            "mode": "groq-ai"
        })
        
    except Exception as e:
        return error(message=str(e), status_code=500)

@router.get("/")
def chat_root():
    return success(message="Chat API is working with Groq AI!")

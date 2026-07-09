from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from models.chat import ChatRequest, ChatResponse
from services.groq_chat import GroqChatService
from crud.chat import save_chat_message, get_chat_history
from core.auth import get_current_user
from utils.response import success, error
from db.supabase import supabase
import json
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    current_user = Depends(get_current_user)
):
    try:
        # Debug: Check if API key is loaded
        api_key = os.getenv("GROQ_API_KEY")
        print(f"GROQ_API_KEY loaded: {api_key is not None}")
        
        # Get quote context if quote_id is provided
        quote_context = None
        if request.quote_id:
            quote = supabase.table("quotes").select("*").eq("id", request.quote_id).eq("user_id", current_user["id"]).execute()
            if quote.data:
                line_items = supabase.table("line_items").select("*").eq("quote_id", request.quote_id).execute()
                quote_context = {
                    "total_amount": quote.data[0].get("total_amount", 0),
                    "contractor_name": quote.data[0].get("contractor_name", "Unknown"),
                    "line_items": line_items.data if line_items.data else []
                }
        
        # Initialize service
        chat_service = GroqChatService(quote_context)
        
        # Get chat history (ignore errors if table doesn't exist)
        history = []
        try:
            history = get_chat_history(current_user["id"])
        except Exception as e:
            print(f"Could not get chat history: {e}")
        
        # Create streaming response
        async def generate():
            full_response = ""
            async for chunk in chat_service.chat_stream(request.message, history):
                full_response += chunk
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            # Save to database (ignore errors if table doesn't exist)
            try:
                save_chat_message(
                    user_id=current_user["id"],
                    message=request.message,
                    response=full_response,
                    quote_id=request.quote_id
                )
            except Exception as e:
                print(f"Could not save chat message: {e}")
            
            yield f"data: {json.dumps({'done': True})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        print(f"Chat error: {str(e)}")
        return error(message=str(e), status_code=500)

@router.get("/history")
def get_history(
    current_user = Depends(get_current_user),
    limit: int = 50
):
    """Get chat history for current user"""
    try:
        history = get_chat_history(current_user["id"], limit)
        return success(data=history)
    except Exception as e:
        return success(data=[])  # Return empty list instead of error

@router.get("/")
def chat_root():
    return success(message="Chat API is working with Groq AI!")

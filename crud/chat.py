from db.supabase import supabase
from datetime import datetime
import os

def save_chat_message(user_id: str, message: str, response: str, quote_id: str = None):
    """Save chat message to database"""
    try:
        data = {
            "user_id": user_id,
            "message": message,
            "response": response,
            "quote_id": quote_id,
            "created_at": datetime.now().isoformat()
        }
        result = supabase.table("chat_history").insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error saving chat: {e}")
        return None

def get_chat_history(user_id: str, limit: int = 50):
    """Get chat history for a user"""
    try:
        result = supabase.table("chat_history")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error getting chat history: {e}")
        return []

def get_chat_history_by_quote(user_id: str, quote_id: str):
    """Get chat history for a specific quote"""
    try:
        result = supabase.table("chat_history")\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("quote_id", quote_id)\
            .order("created_at", desc=True)\
            .execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error getting chat history by quote: {e}")
        return []

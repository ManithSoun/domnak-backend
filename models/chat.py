from pydantic import BaseModel
from typing import Optional, List, Dict

class ChatRequest(BaseModel):
    message: str
    user_id: str
    quote_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    user_id: str
    message: str
    mode: str = "groq-ai"

class ChatHistory(BaseModel):
    user_id: str
    quote_id: Optional[str] = None
    messages: List[Dict[str, str]] = []

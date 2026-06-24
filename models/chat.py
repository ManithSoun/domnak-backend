from pydantic import BaseModel

class ChatRequest(BaseModel):
  quote_id: str
  message: str 
  history: list = []
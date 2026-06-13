from pydantic import BaseModel
from typing import Optional

class QuoteRequest(BaseModel):
  user_id: str
  contractor_name: Optional[str] = None
  total_amount: float
from pydantic import BaseModel
from typing import Optional

class QuoteRequest(BaseModel):
  contractor_name: Optional[str] = None
  total_amount: float
from pydantic import BaseModel
from typing import Optional

class QuoteRequest(BaseModel):
    contractor_name: str
    total_amount: float

class QuoteUpdateRequest(BaseModel):
    contractor_name: Optional[str] = None
    total_amount: Optional[float] = None

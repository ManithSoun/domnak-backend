from pydantic import BaseModel, field_validator
from typing import Optional

class QuoteRequest(BaseModel):
  contractor_name: Optional[str] = None
  total_amount: float
  
  @field_validator('contractor_name')
  @classmethod
  def validation_contractor_name(cls, value):
    if value is not None and len(value) < 3:
      raise ValueError("Contractor name must be at least 3 characters")
    return value
  
  @field_validator('total_amount')
  @classmethod
  def validation_total_amount(cls, value):
    if value <= 0:
      raise ValueError("Total amount must be greater than 0")
    return value
from pydantic import BaseModel, field_validator
from typing import Optional

class BaseQuoteRequest(BaseModel):

    @field_validator('contractor_name', mode='before')
    @classmethod
    def validate_contractor_name(cls, value):
        if value is not None and len(value) < 3:
            raise ValueError("Contractor name must be at least 3 characters")
        return value

    @field_validator('total_amount', mode='before')
    @classmethod
    def validate_total_amount(cls, value):
        if value is not None and value <= 0:
            raise ValueError("Total amount must be greater than 0")
        return value


class QuoteRequest(BaseQuoteRequest):
    contractor_name: Optional[str] = None
    total_amount: float


class QuoteUpdateRequest(BaseQuoteRequest):
    contractor_name: Optional[str] = None
    total_amount: Optional[float] = None
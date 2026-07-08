from pydantic import BaseModel, field_validator
from typing import Optional

class BaseQuoteRequest(BaseModel):

    @field_validator('contractor_name', mode='before', check_fields=False)
    @classmethod
    def validate_contractor_name(cls, value):
        if value is not None and len(value) < 3:
            raise ValueError("Contractor name must be at least 3 characters")
        return value

    @field_validator('total_amount', mode='before', check_fields=False)
    @classmethod
    def validate_total_amount(cls, value):
        if value is not None and value <= 0:
            raise ValueError("Total amount must be greater than 0")
        return value

    @field_validator('quality_tier', mode='before', check_fields=False)
    @classmethod
    def validate_quality_tier(cls, value):
        if value is not None and value not in ['basic', 'standard', 'premium']:
            raise ValueError("Quality tier must be 'basic', 'standard', or 'premium'")
        return value


class QuoteRequest(BaseQuoteRequest):
    contractor_name: Optional[str] = None  
    total_amount: float                      
    quality_tier: Optional[str] = "standard" 


class QuoteUpdateRequest(BaseQuoteRequest):
    contractor_name: Optional[str] = None
    total_amount: Optional[float] = None
    quality_tier: Optional[str] = None
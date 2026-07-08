from pydantic import BaseModel, field_validator
from typing import Optional

class BaseLineItemRequest(BaseModel):

    @field_validator('quantity', mode='before', check_fields=False)
    @classmethod
    def validate_quantity(cls, value):
        if value is not None and value <= 0:
            raise ValueError("Quantity must be greater than 0")
        return value

    @field_validator('unit_price', mode='before', check_fields=False)
    @classmethod
    def validate_unit_price(cls, value):
        if value is not None and value <= 0:
            raise ValueError("Unit price must be greater than 0")
        return value

    @field_validator('total_price', mode='before', check_fields=False)
    @classmethod
    def validate_total_price(cls, value):
        if value is not None and value <= 0:
            raise ValueError("Total price must be greater than 0")
        return value

    @field_validator('unit', mode='before', check_fields=False)
    @classmethod
    def validate_unit(cls, value):
        if value is None:
            return value
        valid_units = ['bag', 'm²', 'm³', 'ton', 'meter', 'liter', 'set', 'roll', 'kg', 'pcs', 'bf']
        if value not in valid_units:
            raise ValueError(f"Unit must be one of: {', '.join(valid_units)}")
        return value


class LineItemRequest(BaseLineItemRequest):
    quote_id: str
    material_name: str
    quantity: float
    unit: str
    unit_price: float
    total_price: Optional[float] = None


class LineItemUpdateRequest(BaseLineItemRequest):
    material_name: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    unit_price: Optional[float] = None
    total_price: Optional[float] = None
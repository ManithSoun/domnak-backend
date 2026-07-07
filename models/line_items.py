from pydantic import BaseModel
from typing import Optional

class LineItemRequest(BaseModel):
    quote_id: str
    material_name: str
    quantity: float
    unit: str
    unit_price: float
    total_price: float

class LineItemUpdateRequest(BaseModel):
    material_name: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    unit_price: Optional[float] = None
    total_price: Optional[float] = None

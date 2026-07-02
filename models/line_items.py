from pydantic import BaseModel, field_validator
from typing import Optional

class LineItemRequest(BaseModel):
  quote_id: str
  material_name: str
  quantity: float
  unit: str
  unit_price: float
  total_price: Optional[float] = None
  
  @field_validator('quantity')
  @classmethod
  def validation_quantity(cls, value):
    if value <= 0:
      raise ValueError("Quantity must be greater than 0")
    return value
  
  @field_validator('unit_price')
  @classmethod
  def validation_unit_price(cls, value):
    if value <= 0:
      raise ValueError("Unit price must be greater than 0")
    return value
  
  @field_validator('total_price')
  @classmethod
  def validation_total_price(cls, value):
    if value is not None and value <= 0:
      raise ValueError("Total price must be greater than 0")
    return value
  
class LineItemUpdateRequest(BaseModel):
  material_name: Optional[str] = None
  quantity: Optional[float] = None
  unit: Optional[str] = None
  unit_price: Optional[float] = None
  total_price: Optional[float] = None
  
  @field_validator('quantity')
  @classmethod
  def validation_quantity(cls, value):
    if value is not None and value <= 0:
      raise ValueError("Quantity must be greater than 0")
    return value
  
  @field_validator('unit_price')
  @classmethod
  def validation_unit_price(cls, value):
    if value is not None and value <= 0:
      raise ValueError("Unit price must be greater than 0")
    return value
  
  @field_validator('total_price')
  @classmethod
  def validation_total_price(cls, value):
    if value is not None and value <= 0:
      raise ValueError("Total price must be greater than 0")
    return value
  
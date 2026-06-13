from pydantic import BaseModel

class LineItemRequest(BaseModel):
  quote_id: str
  material_name: str
  quantity: float
  unit: str
  unit_price: float
  total_price: float
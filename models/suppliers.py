from pydantic import BaseModel

class SupplierRequest(BaseModel):
  name: str
  material_name: str
  location: str 
  phone: str 
  price_per_unit: float
  unit: str
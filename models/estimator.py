from pydantic import BaseModel

class EstimatorRequest(BaseModel):
  floor_area: float
  storeys: int
  finishing: str
  roof_type: str
  location: str
  
  
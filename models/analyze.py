from pydantic import BaseModel
from typing import Optional

class AnalysisResult(BaseModel):
  material_name: str
  quantity: float
  unit: str
  quoted_price: float
  market_price: float
  verdict: str  #fair, overpriced, slightly_high
  overprice_percent: float
  explanation: str
  negotiation_tip: Optional[str] = None
  
  
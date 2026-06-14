from fastapi import APIRouter
from services.supabase import supabase
from models.estimator import EstimatorRequest

router = APIRouter()

rates = {
    "1": {
        "basic":    {"min": 220, "max": 280},
        "standard": {"min": 300, "max": 380},
        "premium":  {"min": 420, "max": 550}
    },
    "2": {
        "basic":    {"min": 260, "max": 320},
        "standard": {"min": 340, "max": 420},
        "premium":  {"min": 460, "max": 600}
    }
}

location_multiplier = {
    "phnom_penh": 1.0,
    "province": 0.90
}

roof_adjustment = {
    "flat": 0,
    "pitched": +15,
    "metal": -10
}

@router.post("/")
def estimation_cost(data: EstimatorRequest):
  rate = rates[str(data.storeys)][data.finishing]
  multiplier = location_multiplier[data.location]
  roof_adj = roof_adjustment[data.roof_type]
  
  min_cost = round((data.floor_area * rate["min"] * multiplier) + (roof_adj * data.floor_area))
  max_cost = round((data.floor_area * rate["max"] * multiplier) + (roof_adj * data.floor_area))
  
  return {
    "min_cost": min_cost,
    "max_cost": max_cost,
    "floor_area": data.floor_area,
    "finishing": data.finishing,
    "location": data.location,
    "rate_per_m2": rate
  }
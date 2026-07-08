from fastapi import APIRouter, Depends
from pydantic import BaseModel
from core.auth import get_current_user
from utils.response import success, error
from typing import Optional
from db.supabase import supabase

router = APIRouter()

class BOQRequest(BaseModel):
    floor_area: float
    building_type: str = "residential"
    storeys: int = 1
    finishing: str = "standard"
    quote_id: Optional[str] = None

@router.post("/calculate")
def calculate_boq(
    data: BOQRequest,
    current_user = Depends(get_current_user)
):
    """Calculate Bill of Quantities for a building"""
    try:
        rates = {
            "residential": {
                "cement_bags": 0.5, "steel_kg": 20, "bricks": 120,
                "sand_cubic": 0.05, "gravel_cubic": 0.04, "paint_liters": 0.2,
                "tiles_sqm": 0.8, "electrical_wire_m": 5, "pvc_pipes_m": 0.5
            },
            "commercial": {
                "cement_bags": 0.6, "steel_kg": 30, "bricks": 130,
                "sand_cubic": 0.06, "gravel_cubic": 0.05, "paint_liters": 0.25,
                "tiles_sqm": 0.9, "electrical_wire_m": 7, "pvc_pipes_m": 0.7
            },
            "villa": {
                "cement_bags": 0.7, "steel_kg": 35, "bricks": 150,
                "sand_cubic": 0.07, "gravel_cubic": 0.06, "paint_liters": 0.3,
                "tiles_sqm": 1.0, "electrical_wire_m": 8, "pvc_pipes_m": 0.8
            }
        }
        
        finishing_multiplier = {"basic": 1.0, "standard": 1.2, "premium": 1.5}
        
        building_rates = rates.get(data.building_type, rates["residential"])
        multiplier = finishing_multiplier.get(data.finishing, 1.2)
        total_area = data.floor_area * data.storeys
        
        quantities = {}
        for material, rate in building_rates.items():
            quantities[material] = round(rate * total_area * multiplier, 2)
        
        prices = {
            "cement_bags": 8.50, "steel_kg": 0.85, "bricks": 0.08,
            "sand_cubic": 45, "gravel_cubic": 40, "paint_liters": 12,
            "tiles_sqm": 15, "electrical_wire_m": 2.5, "pvc_pipes_m": 3
        }
        
        cost_breakdown = {}
        for material, qty in quantities.items():
            cost_breakdown[material] = round(qty * prices.get(material, 0), 2)
        
        total_material_cost = sum(cost_breakdown.values())
        labor_cost = round(total_material_cost * 0.35, 2)
        total_cost = round(total_material_cost + labor_cost, 2)
        
        # Map material names for display
        material_names = {
            "cement_bags": "Cement", "steel_kg": "Steel", "bricks": "Bricks",
            "sand_cubic": "Sand", "gravel_cubic": "Gravel", "paint_liters": "Paint",
            "tiles_sqm": "Tiles", "electrical_wire_m": "Electrical Wire", "pvc_pipes_m": "PVC Pipes"
        }
        
        formatted_quantities = {}
        for key, value in quantities.items():
            formatted_quantities[material_names.get(key, key)] = value
        
        formatted_costs = {}
        for key, value in cost_breakdown.items():
            formatted_costs[material_names.get(key, key)] = value
        
        return success(data={
            "project_details": {
                "floor_area": data.floor_area,
                "storeys": data.storeys,
                "total_area": total_area,
                "building_type": data.building_type,
                "finishing": data.finishing
            },
            "quantities": formatted_quantities,
            "cost_breakdown": formatted_costs,
            "labor_cost": labor_cost,
            "total_material_cost": round(total_material_cost, 2),
            "total_estimated_cost": total_cost,
            "cost_per_sqm": round(total_cost / total_area, 2) if total_area > 0 else 0
        })
        
    except Exception as e:
        return error(message=str(e), status_code=500)

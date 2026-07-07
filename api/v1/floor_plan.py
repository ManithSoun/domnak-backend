from fastapi import APIRouter, Depends, UploadFile, File
from core.auth import get_current_user
from utils.response import success, error
from PIL import Image
import io
import base64
import os
import json
from groq import Groq
from db.supabase import supabase
from datetime import datetime

router = APIRouter()

# Cambodia material rates (per sqm)
MATERIAL_RATES = {
    "cement_bags": {"rate": 0.5, "price": 8.50, "unit": "bag"},
    "steel_kg": {"rate": 20, "price": 0.85, "unit": "kg"},
    "bricks": {"rate": 120, "price": 0.08, "unit": "pcs"},
    "sand_cubic_meters": {"rate": 0.05, "price": 45, "unit": "m³"},
    "gravel_cubic_meters": {"rate": 0.04, "price": 40, "unit": "m³"},
    "paint_liters": {"rate": 0.2, "price": 12, "unit": "liter"},
    "tiles_sqm": {"rate": 0.8, "price": 15, "unit": "m²"},
    "electrical_wire_m": {"rate": 5, "price": 2.5, "unit": "meter"},
    "pvc_pipes_m": {"rate": 0.5, "price": 3, "unit": "meter"}
}

@router.post("/upload")
async def upload_floor_plan(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """Upload floor plan and extract rooms using AI Vision"""
    try:
        if not file.content_type.startswith('image/'):
            return error(message="File must be an image", status_code=400)
        
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        prompt = """
        Analyze this floor plan and extract the following in JSON format:
        
        1. List all rooms with:
           - name (Living Room, Bedroom, Kitchen, Bathroom, etc.)
           - width in meters (estimate from scale if present)
           - length in meters
           - area in square meters
        
        2. Total floor area in square meters
        
        3. Building type (residential/commercial/villa)
        
        4. Number of floors
        
        5. Special features (balcony, terrace, garden, etc.)
        
        Return ONLY valid JSON with no extra text:
        {
            "building_type": "residential",
            "floors": 1,
            "rooms": [
                {"name": "Living Room", "width": 5.0, "length": 6.0, "area": 30.0},
                {"name": "Kitchen", "width": 4.0, "length": 3.5, "area": 14.0}
            ],
            "total_area": 100.0,
            "features": ["balcony"],
            "scale_used": "approx"
        }
        """
        
        completion = client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
                    ]
                }
            ],
            temperature=0.3,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        try:
            analysis = json.loads(completion.choices[0].message.content)
        except:
            analysis = {
                "rooms": [],
                "total_area": 0,
                "building_type": "residential",
                "floors": 1,
                "features": []
            }
        
        total_area = analysis.get("total_area", 0)
        boq = generate_boq(total_area)
        
        floor_plan_data = {
            "user_id": current_user.id,
            "file_name": file.filename,
            "analysis": analysis,
            "boq": boq,
            "total_area": total_area,
            "created_at": datetime.now().isoformat()
        }
        
        try:
            result = supabase.table("floor_plans").insert(floor_plan_data).execute()
            floor_plan_id = result.data[0]["id"] if result.data else None
        except:
            floor_plan_id = None
        
        return success(data={
            "floor_plan_id": floor_plan_id,
            "analysis": analysis,
            "boq": boq,
            "total_area": total_area,
            "rooms_count": len(analysis.get("rooms", [])),
            "message": "Floor plan analyzed successfully"
        })
        
    except Exception as e:
        return error(message=str(e), status_code=500)

def generate_boq(total_area):
    """Generate Bill of Quantities from total area"""
    if total_area <= 0:
        return {"error": "Invalid area"}
    
    quantities = {}
    cost_breakdown = {}
    
    for material, data in MATERIAL_RATES.items():
        qty = round(total_area * data["rate"], 2)
        quantities[material] = {
            "quantity": qty,
            "unit": data["unit"],
            "price_per_unit": data["price"],
            "total_cost": round(qty * data["price"], 2)
        }
        cost_breakdown[material] = round(qty * data["price"], 2)
    
    total_material_cost = sum(cost_breakdown.values())
    labor_cost = round(total_material_cost * 0.35, 2)
    
    return {
        "quantities": quantities,
        "cost_breakdown": cost_breakdown,
        "labor_cost": labor_cost,
        "total_material_cost": round(total_material_cost, 2),
        "total_estimated_cost": round(total_material_cost + labor_cost, 2),
        "cost_per_sqm": round((total_material_cost + labor_cost) / total_area, 2) if total_area > 0 else 0
    }

@router.post("/create-quote")
async def create_quote_from_floor_plan(
    file: UploadFile = File(...),
    contractor_name: str = None,
    current_user = Depends(get_current_user)
):
    """Upload floor plan and auto-create quote with line items"""
    try:
        result = await upload_floor_plan(file, current_user)
        if result.get("error"):
            return result
        
        data = result["data"]
        analysis = data["analysis"]
        boq = data["boq"]
        total_area = data["total_area"]
        
        quote_data = {
            "user_id": current_user.id,
            "contractor_name": contractor_name or f"AI Generated - {total_area}m²",
            "total_amount": boq["total_estimated_cost"],
            "status": "pending",
            "quality_tier": "standard",
            "project_name": f"Floor Plan - {total_area}m²"
        }
        
        quote_result = supabase.table("quotes").insert(quote_data).execute()
        if not quote_result.data:
            return error(message="Failed to create quote", status_code=500)
            
        quote_id = quote_result.data[0]["id"]
        
        line_items_created = 0
        for material, item_data in boq["quantities"].items():
            if item_data["quantity"] > 0:
                line_item = {
                    "quote_id": quote_id,
                    "material_name": material.replace("_", " ").title(),
                    "quantity": item_data["quantity"],
                    "unit": item_data["unit"],
                    "unit_price": item_data["price_per_unit"],
                    "total_price": item_data["total_cost"]
                }
                supabase.table("line_items").insert(line_item).execute()
                line_items_created += 1
        
        return success(data={
            "quote_id": quote_id,
            "contractor_name": quote_data["contractor_name"],
            "total_amount": boq["total_estimated_cost"],
            "total_area": total_area,
            "rooms_count": len(analysis.get("rooms", [])),
            "line_items_created": line_items_created,
            "boq": boq,
            "message": "Quote created successfully from floor plan"
        })
        
    except Exception as e:
        return error(message=str(e), status_code=500)

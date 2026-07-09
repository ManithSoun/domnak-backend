from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from core.auth import get_current_user
from utils.response import success, error
from services.floor_plan_service import FloorPlanService
from db.supabase import supabase
from datetime import datetime

router = APIRouter()
floor_plan_service = FloorPlanService()

@router.post("/upload")
async def upload_floor_plan(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """Upload a floor plan image and get BOQ analysis"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            return error(message="File must be an image", status_code=400)
        
        # Read file
        contents = await file.read()
        
        # Process floor plan
        result = floor_plan_service.process_floor_plan(contents)
        
        if not result:
            return error(message="Failed to process floor plan", status_code=500)
        
        # Save to database
        floor_plan_data = {
            "user_id": current_user["id"],
            "file_name": file.filename,
            "analysis": result["analysis"],
            "boq": result["boq"],
            "total_area": result["total_area"],
            "created_at": datetime.now().isoformat()
        }
        
        try:
            db_result = supabase.table("floor_plans").insert(floor_plan_data).execute()
            floor_plan_id = db_result.data[0]["id"] if db_result.data else None
        except Exception as e:
            print(f"Database save error: {e}")
            floor_plan_id = None
        
        return success(data={
            "floor_plan_id": floor_plan_id,
            "analysis": result["analysis"],
            "boq": result["boq"],
            "total_area": result["total_area"],
            "rooms_count": result["rooms_count"],
            "message": "Floor plan analyzed successfully"
        })
        
    except Exception as e:
        return error(message=str(e), status_code=500)

@router.post("/create-quote")
async def create_quote_from_floor_plan(
    file: UploadFile = File(...),
    contractor_name: str = None,
    current_user = Depends(get_current_user)
):
    """Upload floor plan and automatically create a quote with line items"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            return error(message="File must be an image", status_code=400)
        
        # Read and process
        contents = await file.read()
        result = floor_plan_service.process_floor_plan(contents)
        
        if not result:
            return error(message="Failed to process floor plan", status_code=500)
        
        analysis = result["analysis"]
        boq = result["boq"]
        total_area = result["total_area"]
        
        # Create quote
        quote_data = {
            "user_id": current_user["id"],
            "contractor_name": contractor_name or f"Floor Plan - {total_area}m²",
            "total_amount": boq["total_estimated_cost"],
            "status": "pending",
            "quality_tier": "standard",
            "project_name": f"Floor Plan - {total_area}m²"
        }
        
        quote_result = supabase.table("quotes").insert(quote_data).execute()
        if not quote_result.data:
            return error(message="Failed to create quote", status_code=500)
        
        quote_id = quote_result.data[0]["id"]
        
        # Create line items from BOQ
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

@router.get("/{floor_plan_id}")
def get_floor_plan(
    floor_plan_id: str,
    current_user = Depends(get_current_user)
):
    """Get saved floor plan analysis"""
    try:
        result = supabase.table("floor_plans").select("*").eq("id", floor_plan_id).eq("user_id", current_user["id"]).execute()
        if not result.data or len(result.data) == 0:
            return error(message="Floor plan not found or access denied", status_code=404)
        
        return success(data=result.data[0])
        
    except Exception as e:
        return error(message=str(e), status_code=500)

@router.delete("/{floor_plan_id}")
def delete_floor_plan(
    floor_plan_id: str,
    current_user = Depends(get_current_user)
):
    """Delete a floor plan"""
    try:
        # Check if floor plan exists and belongs to user
        result = supabase.table("floor_plans").select("id").eq("id", floor_plan_id).eq("user_id", current_user["id"]).execute()
        if not result.data or len(result.data) == 0:
            return error(message="Floor plan not found or access denied", status_code=404)
        
        # Delete the floor plan
        supabase.table("floor_plans").delete().eq("id", floor_plan_id).eq("user_id", current_user["id"]).execute()
        
        return success(message="Floor plan deleted successfully")
        
    except Exception as e:
        return error(message=str(e), status_code=500)

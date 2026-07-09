from fastapi import APIRouter, Depends, Query
from db.supabase import supabase
from models.line_items import LineItemRequest, LineItemUpdateRequest
from core.auth import get_current_user
import crud.line_items as line_item_crud
from utils.response import success, error
from typing import Optional

router = APIRouter()

@router.post("/")
def create_line_item(data: LineItemRequest, current_user = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        
        # Verify quote ownership
        quote = supabase.table("quotes").select("id").eq("id", data.quote_id).eq("user_id", user_id).execute()
        if not quote.data or len(quote.data) == 0:
            return error(message="Quote not found or access denied", status_code=403)
        
        # Calculate total_price if not provided
        total_price = data.total_price
        if total_price is None or total_price == 0:
            total_price = data.quantity * data.unit_price
        
        result = line_item_crud.create_line_item(
            data.quote_id,
            data.material_name,
            data.quantity,
            data.unit,
            data.unit_price,
            total_price
        )
        return success(data=result)
    except Exception as e:
        return error(message=str(e), status_code=500)

@router.get("/")
def get_line_items(
    quote_id: str = Query(...),
    current_user = Depends(get_current_user)
):
    try:
        user_id = current_user["id"]
        # Verify quote ownership
        quote = supabase.table("quotes").select("id").eq("id", quote_id).eq("user_id", user_id).execute()
        if not quote.data or len(quote.data) == 0:
            return error(message="Quote not found or access denied", status_code=403)
        
        result = line_item_crud.get_line_items(quote_id)
        return success(data=result)
    except Exception as e:
        return error(message=str(e), status_code=500)

@router.get("/{item_id}")
def get_single_line_item(item_id: str, current_user = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        # Get line item
        item = supabase.table("line_items").select("*").eq("id", item_id).execute()
        if not item.data or len(item.data) == 0:
            return error(message="Line item not found", status_code=404)
        
        # Verify quote ownership
        quote = supabase.table("quotes").select("id").eq("id", item.data[0]["quote_id"]).eq("user_id", user_id).execute()
        if not quote.data or len(quote.data) == 0:
            return error(message="Access denied", status_code=403)
        
        return success(data=item.data[0])
    except Exception as e:
        return error(message=str(e), status_code=500)

@router.patch("/{item_id}")
def update_line_item(item_id: str, data: LineItemUpdateRequest, current_user = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        
        # Get current line item
        current_item = supabase.table("line_items").select("*").eq("id", item_id).execute()
        if not current_item.data or len(current_item.data) == 0:
            return error(message="Line item not found", status_code=404)
        
        current = current_item.data[0]
        
        # Verify quote ownership
        quote = supabase.table("quotes").select("id").eq("id", current["quote_id"]).eq("user_id", user_id).execute()
        if not quote.data or len(quote.data) == 0:
            return error(message="Access denied", status_code=403)
        
        # Use current values if not provided in update
        material_name = data.material_name if data.material_name is not None else current["material_name"]
        quantity = data.quantity if data.quantity is not None else current["quantity"]
        unit = data.unit if data.unit is not None else current["unit"]
        unit_price = data.unit_price if data.unit_price is not None else current["unit_price"]
        
        # Calculate total_price
        if data.total_price is not None and data.total_price > 0:
            total_price = data.total_price
        else:
            total_price = quantity * unit_price
        
        result = line_item_crud.update_line_item(
            item_id,
            material_name,
            quantity,
            unit,
            unit_price,
            total_price
        )
        return success(data=result)
    except Exception as e:
        return error(message=str(e), status_code=500)

@router.delete("/{item_id}")
def delete_line_item(item_id: str, current_user = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        # Get line item
        item = supabase.table("line_items").select("quote_id").eq("id", item_id).execute()
        if not item.data or len(item.data) == 0:
            return error(message="Line item not found", status_code=404)
        
        # Verify quote ownership
        quote = supabase.table("quotes").select("id").eq("id", item.data[0]["quote_id"]).eq("user_id", user_id).execute()
        if not quote.data or len(quote.data) == 0:
            return error(message="Access denied", status_code=403)
        
        line_item_crud.delete_line_item(item_id)
        return success(message="Line item deleted")
    except Exception as e:
        return error(message=str(e), status_code=500)

from fastapi import APIRouter, Depends
from db.supabase import supabase
from models.line_items import LineItemRequest, LineItemUpdateRequest
from core.auth import get_current_user
import crud.line_items as line_item_crud
from utils.response import success, error

router = APIRouter()

@router.post("/")
def create_line_item(data: LineItemRequest, current_user = Depends(get_current_user)):
    try:
        quote = supabase.table("quotes").select("id").eq("id", str(data.quote_id)).eq("user_id", current_user.id).execute()
        if not quote.data or len(quote.data) == 0:
            return error(message="Quote not found or access denied", status_code=403)

        result = line_item_crud.create_line_item(
            data.quote_id,
            data.material_name,
            data.quantity,
            data.unit,
            data.unit_price,
            data.total_price
        )
        # Return single object, not array
        return success(data=result[0] if isinstance(result, list) and len(result) > 0 else result)
    except Exception as e:
        return error(message=str(e), status_code=500)

@router.get("/")
def get_line_items(quote_id: str, current_user = Depends(get_current_user)):
    try:
        quote = supabase.table("quotes").select("id").eq("id", quote_id).eq("user_id", current_user.id).execute()
        if not quote.data or len(quote.data) == 0:
            return error(message="Quote not found or access denied", status_code=403)

        result = line_item_crud.get_line_items(quote_id)
        return success(data=result)
    except Exception as e:
        return error(message=str(e), status_code=500)

@router.get("/{item_id}")
def get_line_item(item_id: str, current_user = Depends(get_current_user)):
    try:
        item = supabase.table("line_items").select("*").eq("id", item_id).execute()
        if not item.data or len(item.data) == 0:
            return error(message="Item not found", status_code=404)
        
        quote = supabase.table("quotes").select("id").eq("id", item.data[0]["quote_id"]).eq("user_id", current_user.id).execute()
        if not quote.data or len(quote.data) == 0:
            return error(message="Access denied", status_code=403)
        
        return success(data=item.data[0])
    except Exception as e:
        return error(message=str(e), status_code=500)

@router.delete("/{item_id}")
def delete_line_item(item_id: str, current_user = Depends(get_current_user)):
    try:
        item = supabase.table("line_items").select("quote_id").eq("id", item_id).execute()
        if not item.data or len(item.data) == 0:
            return error(message="Item not found", status_code=404)

        quote = supabase.table("quotes").select("id").eq("id", item.data[0]["quote_id"]).eq("user_id", current_user.id).execute()
        if not quote.data or len(quote.data) == 0:
            return error(message="Access denied", status_code=403)

        line_item_crud.delete_line_item(item_id)
        return success(message="Item deleted")
    except Exception as e:
        return error(message=str(e), status_code=500)

@router.patch("/{item_id}")
def update_line_item(item_id: str, data: LineItemUpdateRequest, current_user = Depends(get_current_user)):
    try:
        item = supabase.table("line_items").select("quote_id").eq("id", item_id).execute()
        if not item.data or len(item.data) == 0:
            return error(message="Item not found", status_code=404)

        quote = supabase.table("quotes").select("id").eq("id", item.data[0]["quote_id"]).eq("user_id", current_user.id).execute()
        if not quote.data or len(quote.data) == 0:
            return error(message="Access denied", status_code=403)

        result = line_item_crud.update_line_item(
            item_id,
            data.material_name,
            data.quantity,
            data.unit,
            data.unit_price,
            data.total_price
        )
        return success(data=result[0] if isinstance(result, list) and len(result) > 0 else result)
    except Exception as e:
        return error(message=str(e), status_code=500)

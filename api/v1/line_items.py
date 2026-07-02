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
        # ownership check
        quote = supabase.table("quotes").select("id").eq("id", data.quote_id).eq("user_id", current_user.id).single().execute()
        if not quote.data:
            return error(message="Quote not found or access denied", status_code=403)

        result = line_item_crud.create_line_item(
            data.quote_id,
            data.material_name,
            data.quantity,
            data.unit,
            data.unit_price,
            data.total_price
        )
        return success(data=result)
    except Exception as e:
        return error(message=str(e), status_code=500)

@router.get("/")
def get_line_items(quote_id: str, current_user = Depends(get_current_user)):
    try:
        # ownership check
        quote = supabase.table("quotes").select("id").eq("id", quote_id).eq("user_id", current_user.id).single().execute()
        if not quote.data:
            return error(message="Quote not found or access denied", status_code=403)

        result = line_item_crud.get_line_items(quote_id)
        return success(data=result)
    except Exception as e:
        return error(message=str(e), status_code=500)

@router.delete("/{item_id}")
def delete_line_item(item_id: str, current_user = Depends(get_current_user)):
    try:
        # get line item to find quote_id
        item = supabase.table("line_items").select("quote_id").eq("id", item_id).single().execute()
        if not item.data:
            return error(message="Item not found", status_code=404)

        # verify quote belongs to current user
        quote = supabase.table("quotes").select("id").eq("id", item.data["quote_id"]).eq("user_id", current_user.id).single().execute()
        if not quote.data:
            return error(message="Access denied", status_code=403)

        line_item_crud.delete_line_item(item_id)
        return success(message="Item deleted")
    except Exception as e:
        return error(message=str(e), status_code=500)

@router.patch("/{item_id}")
def update_line_item(item_id: str, data: LineItemUpdateRequest, current_user = Depends(get_current_user)):
    try:
        # get line item to find quote_id
        item = supabase.table("line_items").select("quote_id").eq("id", item_id).single().execute()
        if not item.data:
            return error(message="Item not found", status_code=404)

        # verify quote belongs to current user
        quote = supabase.table("quotes").select("id").eq("id", item.data["quote_id"]).eq("user_id", current_user.id).single().execute()
        if not quote.data:
            return error(message="Access denied", status_code=403)

        result = line_item_crud.update_line_item(
            item_id,
            data.material_name,
            data.quantity,
            data.unit,
            data.unit_price,
            data.total_price
        )
        return success(data=result)
    except Exception as e:
        return error(message=str(e), status_code=500)
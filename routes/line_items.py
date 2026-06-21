from fastapi import APIRouter, Depends, HTTPException
from models.line_items import LineItemRequest
from services.supabase import supabase
from services.auth import get_current_user

router = APIRouter()

@router.post("/")
def create_line_item(data: LineItemRequest, current_user = Depends(get_current_user)):
  # verify this quote belong to the current user
  quote = supabase.table("quotes").select("id").ep("id", data.quote_id).ep("user_id", current_user.id).single().execute()
  
  if not quote.data:
    raise HTTPException(status_code = 403, detail="Quote not found or access denied")
  
  res = supabase.table("line_items").insert({
    "quote_id": data.quote_id,
    "material_name": data.material_name,
    "quantity": data.quantity,
    "unit": data.unit,
    "unit_price": data.unit_price,
    "total_price": data.total_price
  }).execute()

  return res.data

@router.get("/")
def get_line_item(quote_id: str, current_user = Depends(get_current_user)):
  quote = supabase.table("quotes").select("id").eq("id", quote_id).eq("user_id", current_user.id).single().execute()
  
  if not quote.data:
    raise HTTPException(status_code = 403, detail="Quote not found or access denied")
  
  res = supabase.table("line_items").select("*").eq("quote_id", quote_id).execute()
  return res.data

@router.delete("/{item_id}")
def delete_line_item(item_id: str, current_user = Depends(get_current_user)):
  supabase.table("line_items").delete().eq("id", item_id).execute()
  return {"message": "Item deleted"}
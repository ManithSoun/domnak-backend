from fastapi import APIRouter
from models.line_items import LineItemRequest
from services.supabase import supabase

router = APIRouter()

@router.post("/")
def create_line_item(data: LineItemRequest):
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
def get_line_item(quote_id: str):
  res = supabase.table("line_items").select("*").eq("quote_id", quote_id).execute()

  return res.data

@router.delete("/{item_id}")
def delete_line_item(item_id: str):
  supabase.table("line_items").delete().eq("id", item_id).execute()

  return {"message": "item deleted"}
from fastapi import APIRouter
from models.quotes import QuoteRequest
from services.supabase import supabase

router = APIRouter()

@router.post("/")
def create_quote(data: QuoteRequest):
  res = supabase.table("quotes").insert({
    "user_id": data.user_id,
    "contractor_name": data.contractor_name,
    "total_amount": data.total_amount
  }).execute()

  return res.data

@router.get("/")
def get_quote(user_id: str):
  res = supabase.table("quotes").select("*").eq("user_id", user_id).execute()
  return res.data

@router.delete("/{quote_id}")
def delet_quote(quote_id: str):
  supabase.table("quotes").delete().eq("id", quote_id).execute()

  return {"message": "Deleted"}

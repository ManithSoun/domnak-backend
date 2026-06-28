from fastapi import APIRouter, Depends
from models.quotes import QuoteRequest
from services.supabase import supabase
from services.auth import get_current_user


router = APIRouter()

@router.post("/")
def create_quote(data: QuoteRequest, current_user = Depends(get_current_user)):
  res = supabase.table("quotes").insert({
    "user_id": current_user.id,
    "contractor_name": data.contractor_name,
    "total_amount": data.total_amount
  }).execute()

  return res.data

@router.get("/")
def get_quote(current_user = Depends(get_current_user)):
  res = supabase.table("quotes").select("*").eq("user_id", current_user.id).execute()
  return res.data

@router.delete("/{quote_id}")
def delet_quote(quote_id: str, current_user = Depends(get_current_user)):
  supabase.table("quotes").delete().eq("id", quote_id).eq("user_id", current_user.id).execute()
  return {"message": "Quote Deleted"}

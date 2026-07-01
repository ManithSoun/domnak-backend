from fastapi import APIRouter, Depends
from models.quotes import QuoteRequest
from core.auth import get_current_user
import crud.quotes as quote_crud

router = APIRouter()

@router.post("/")
def create_quote(data: QuoteRequest, current_user = Depends(get_current_user)):
  result = quote_crud.create_quote(current_user.id, data.contractor_name, data.total_amount)
  return result

@router.get("/")
def get_quote(current_user = Depends(get_current_user)):
  result= quote_crud.get_quote(current_user.id)
  return result

@router.delete("/{quote_id}")
def delet_quote(quote_id: str, current_user = Depends(get_current_user)):
  quote_crud.delete_quote(quote_id, current_user.id)
  return {"message": "Quote Deleted"}

from fastapi import APIRouter, Depends
from db.supabase import supabase
from models.quotes import QuoteRequest, QuoteUpdateRequest
from core.auth import get_current_user
import crud.quotes as quote_crud
from utils.response import success, error

router = APIRouter()

@router.post("/")
def create_quote(data: QuoteRequest, current_user = Depends(get_current_user)):
    try:
        result = quote_crud.create_quote(current_user.id, data.contractor_name, data.total_amount)
        return success(data=result)
    except Exception as e:
        return error(message=str(e), status_code=500)

@router.get("/")
def get_quotes(current_user = Depends(get_current_user)):
    try:
        result = quote_crud.get_quote(current_user.id)
        return success(data=result)
    except Exception as e:
        return error(message=str(e), status_code=500)

@router.get("/{quote_id}")
def get_quote(quote_id: str, current_user = Depends(get_current_user)):
    try:
        quote = supabase.table("quotes").select("*").eq("id", quote_id).eq("user_id", current_user.id).single().execute()
        if not quote.data:
            return error(message="Quote not found or access denied", status_code=403)
        return success(data=quote.data)
    except Exception as e:
        return error(message=str(e), status_code=500)

@router.delete("/{quote_id}")
def delete_quote(quote_id: str, current_user = Depends(get_current_user)):
    try:
        quote = supabase.table("quotes").select("id").eq("id", quote_id).eq("user_id", current_user.id).single().execute()
        if not quote.data:
            return error(message="Quote not found or access denied", status_code=403)
        quote_crud.delete_quote(quote_id, current_user.id)
        return success(message="Quote deleted")
    except Exception as e:
        return error(message=str(e), status_code=500)

@router.patch("/{quote_id}")
def update_quote(quote_id: str, data: QuoteUpdateRequest, current_user = Depends(get_current_user)):
    try:
        quote = supabase.table("quotes").select("id").eq("id", quote_id).eq("user_id", current_user.id).single().execute()
        if not quote.data:
            return error(message="Quote not found or access denied", status_code=403)
        result = quote_crud.update_quote(
            quote_id,
            current_user.id,
            data.contractor_name,
            data.total_amount
        )
        return success(data=result)
    except Exception as e:
        return error(message=str(e), status_code=500)
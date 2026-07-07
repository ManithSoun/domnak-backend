from fastapi import APIRouter, Depends, Query
from db.supabase import supabase
from models.quotes import QuoteRequest, QuoteUpdateRequest
from core.auth import get_current_user
import crud.quotes as quote_crud
from utils.response import success, error
from typing import Optional

router = APIRouter()

@router.post("/")
def create_quote(data: QuoteRequest, current_user = Depends(get_current_user)):
    try:
        user_id = current_user.get('id') or current_user['id']
        result = quote_crud.create_quote(user_id, data.contractor_name, data.total_amount)
        return success(data=result)
    except Exception as e:
        return error(message=str(e), status_code=500)

@router.get("/")
def get_quotes(
    quote_id: Optional[str] = Query(None),
    current_user = Depends(get_current_user)
):
    try:
        user_id = current_user.get('id') or current_user['id']
        if quote_id:
            quote = supabase.table("quotes").select("*").eq("id", quote_id).eq("user_id", user_id).execute()
            if not quote.data or len(quote.data) == 0:
                return error(message="Quote not found or access denied", status_code=403)
            return success(data=quote.data[0])
        else:
            result = quote_crud.get_quote(user_id)
            return success(data=result)
    except Exception as e:
        return error(message=str(e), status_code=500)

# 🔥 FIX: Added GET method for single quote
@router.get("/{quote_id}")
def get_single_quote(quote_id: str, current_user = Depends(get_current_user)):
    try:
        user_id = current_user.get('id') or current_user['id']
        quote = supabase.table("quotes").select("*").eq("id", quote_id).eq("user_id", user_id).execute()
        if not quote.data or len(quote.data) == 0:
            return error(message="Quote not found or access denied", status_code=403)
        return success(data=quote.data[0])
    except Exception as e:
        return error(message=str(e), status_code=500)

@router.patch("/{quote_id}")
def update_quote(quote_id: str, data: QuoteUpdateRequest, current_user = Depends(get_current_user)):
    try:
        user_id = current_user.get('id') or current_user['id']
        quote = supabase.table("quotes").select("id").eq("id", quote_id).eq("user_id", user_id).execute()
        if not quote.data or len(quote.data) == 0:
            return error(message="Quote not found or access denied", status_code=403)
        result = quote_crud.update_quote(
            quote_id,
            user_id,
            data.contractor_name,
            data.total_amount
        )
        return success(data=result)
    except Exception as e:
        return error(message=str(e), status_code=500)

@router.delete("/{quote_id}")
def delete_quote(quote_id: str, current_user = Depends(get_current_user)):
    try:
        user_id = current_user.get('id') or current_user['id']
        quote = supabase.table("quotes").select("id").eq("id", quote_id).eq("user_id", user_id).execute()
        if not quote.data or len(quote.data) == 0:
            return error(message="Quote not found or access denied", status_code=403)
        quote_crud.delete_quote(quote_id, user_id)
        return success(message="Quote deleted")
    except Exception as e:
        return error(message=str(e), status_code=500)

@router.get("/{quote_id}/share")
def get_shareable_link(quote_id: str, current_user = Depends(get_current_user)):
    try:
        user_id = current_user.get('id') or current_user['id']
        quote = supabase.table("quotes").select("*").eq("id", quote_id).eq("user_id", user_id).execute()
        if not quote.data or len(quote.data) == 0:
            return error(message="Quote not found or access denied", status_code=403)
        
        if not quote.data[0].get("share_token"):
            import uuid
            share_token = str(uuid.uuid4())[:8]
            supabase.table("quotes").update({"share_token": share_token}).eq("id", quote_id).execute()
        else:
            share_token = quote.data[0]["share_token"]
        
        share_link = f"https://domnak.vercel.app/share/{share_token}"
        
        return success(data={
            "share_token": share_token,
            "share_link": share_link,
            "expires_in": "7 days",
            "quote_id": quote_id
        })
        
    except Exception as e:
        return error(message=str(e), status_code=500)

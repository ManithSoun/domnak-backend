from fastapi import APIRouter, Depends, Query
from db.supabase import supabase
from models.quotes import QuoteRequest, QuoteUpdateRequest
from core.auth import get_current_user
import crud.quotes as quote_crud
from utils.response import success, error
from typing import Optional

router = APIRouter()

def parse_float_safe(val) -> float:
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    try:
        cleaned = str(val).replace("$", "").replace(",", "").strip()
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0

def clean_unit(val) -> str:
    if not val:
        return "pcs"
    val = str(val).lower().strip()
    allowed = ["pcs", "bag", "kg", "liter", "meter", "ton", "set"]
    if val in allowed:
        return val
    mapping = {
        "unit": "pcs",
        "units": "pcs",
        "piece": "pcs",
        "pieces": "pcs",
        "box": "pcs",
        "m": "meter",
        "meters": "meter",
        "sqm": "pcs",
        "m2": "pcs",
        "m3": "pcs"
    }
    return mapping.get(val, "pcs")

@router.post("/")
def create_quote(data: QuoteRequest, current_user = Depends(get_current_user)):
    try:
        # Use dictionary key access
        user_id = current_user["id"]
        result = quote_crud.create_quote(user_id, data.contractor_name, data.total_amount)
        
        if result and data.rooms:
            quote_id = result["id"]
            for room in data.rooms:
                material_name = room.get("material_name") or room.get("name")
                if material_name:
                    qty = parse_float_safe(room.get("quantity") or room.get("length"))
                    up = parse_float_safe(room.get("unit_price"))
                    tp = parse_float_safe(room.get("total_price")) or (qty * up)
                    supabase.table("line_items").insert({
                        "quote_id": quote_id,
                        "material_name": material_name,
                        "quantity": qty,
                        "unit": clean_unit(room.get("unit")),
                        "unit_price": up,
                        "total_price": tp
                    }).execute()
            
            # Auto-trigger analysis
            try:
                from api.v1.analysis import analysis_quote
                analysis_quote(quote_id, current_user)
            except Exception as ae:
                print(f"Failed to auto-analyze: {ae}")
                
        return success(data=result)
    except Exception as e:
        return error(message=str(e), status_code=500)

@router.get("/")
def get_quotes(
    quote_id: Optional[str] = Query(None),
    current_user = Depends(get_current_user)
):
    try:
        user_id = current_user["id"]
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

@router.get("/{quote_id}")
def get_single_quote(quote_id: str, current_user = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        quote = supabase.table("quotes").select("*").eq("id", quote_id).eq("user_id", user_id).execute()
        if not quote.data or len(quote.data) == 0:
            return error(message="Quote not found or access denied", status_code=403)
        return success(data=quote.data[0])
    except Exception as e:
        return error(message=str(e), status_code=500)

@router.patch("/{quote_id}")
def update_quote(quote_id: str, data: QuoteUpdateRequest, current_user = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
        quote = supabase.table("quotes").select("id").eq("id", quote_id).eq("user_id", user_id).execute()
        if not quote.data or len(quote.data) == 0:
            return error(message="Quote not found or access denied", status_code=403)
        result = quote_crud.update_quote(
            quote_id,
            user_id,
            data.contractor_name,
            data.total_amount
        )
        
        if data.rooms is not None:
            # Delete old line items
            supabase.table("line_items").delete().eq("quote_id", quote_id).execute()
            # Save new line items
            for room in data.rooms:
                material_name = room.get("material_name") or room.get("name")
                if material_name:
                    qty = parse_float_safe(room.get("quantity") or room.get("length"))
                    up = parse_float_safe(room.get("unit_price"))
                    tp = parse_float_safe(room.get("total_price")) or (qty * up)
                    supabase.table("line_items").insert({
                        "quote_id": quote_id,
                        "material_name": material_name,
                        "quantity": qty,
                        "unit": clean_unit(room.get("unit")),
                        "unit_price": up,
                        "total_price": tp
                    }).execute()
            
            # Auto-trigger analysis
            try:
                from api.v1.analysis import analysis_quote
                analysis_quote(quote_id, current_user)
            except Exception as ae:
                print(f"Failed to auto-analyze: {ae}")
                
        return success(data=result)
    except Exception as e:
        return error(message=str(e), status_code=500)

@router.delete("/{quote_id}")
def delete_quote(quote_id: str, current_user = Depends(get_current_user)):
    try:
        user_id = current_user["id"]
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
        user_id = current_user["id"]
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

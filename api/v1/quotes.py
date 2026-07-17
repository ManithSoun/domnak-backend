from fastapi import APIRouter, Depends, Query, Body
from pydantic import BaseModel
from db.supabase import supabase, supabase_admin
from models.quotes import QuoteRequest, QuoteUpdateRequest
from core.auth import get_current_user
import crud.quotes as quote_crud
from utils.response import success, error
from typing import Optional

router = APIRouter()

class SendQuoteRequest(BaseModel):
    receiver_id: str
    boq_data: Optional[dict] = None
    file_name: Optional[str] = None
    area: Optional[float] = None
    total: Optional[float] = None

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
        result = quote_crud.create_quote(user_id, data.contractor_name, data.total_amount, data.client_id)
        
        if result and data.rooms:
            quote_id = result["id"]
            for room in data.rooms:
                material_name = room.get("material_name") or room.get("name")
                if material_name:
                    qty = parse_float_safe(room.get("quantity") or room.get("length"))
                    up = parse_float_safe(room.get("unit_price"))
                    tp = parse_float_safe(room.get("total_price")) or (qty * up)
                    supabase_admin.table("line_items").insert({
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
    print("=== GET_QUOTES: reached! User:", current_user)
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
        quote = supabase_admin.table("quotes").select("id").eq("id", quote_id).eq("user_id", user_id).execute()
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
            supabase_admin.table("line_items").delete().eq("quote_id", quote_id).execute()
            # Save new line items
            for room in data.rooms:
                material_name = room.get("material_name") or room.get("name")
                if material_name:
                    qty = parse_float_safe(room.get("quantity") or room.get("length"))
                    up = parse_float_safe(room.get("unit_price"))
                    tp = parse_float_safe(room.get("total_price")) or (qty * up)
                    supabase_admin.table("line_items").insert({
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
        quote = supabase_admin.table("quotes").select("id").eq("id", quote_id).eq("user_id", user_id).execute()
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
        quote = supabase_admin.table("quotes").select("*").eq("id", quote_id).eq("user_id", user_id).execute()
        if not quote.data or len(quote.data) == 0:
            return error(message="Quote not found or access denied", status_code=403)
        
        if not quote.data[0].get("share_token"):
            import uuid
            share_token = str(uuid.uuid4())[:8]
            supabase_admin.table("quotes").update({"share_token": share_token}).eq("id", quote_id).execute()
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


@router.post("/send")
def send_quote_to_client(
    data: SendQuoteRequest,
    current_user = Depends(get_current_user)
):
    """Send a quote to a homeowner client"""
    import logging
    logger = logging.getLogger("domnak")
    
    try:
        sender_id = current_user["id"]
        receiver_id = data.receiver_id
        boq_data = data.boq_data if data.boq_data is not None else {}
        file_name = data.file_name
        area = data.area
        total = data.total
        
        if not receiver_id:
            return error(message="receiver_id is required", status_code=400)
        
        # Create quote record
        # Get contractor name from user metadata
        contractor_name = current_user.get("user_metadata", {}).get("full_name", "Contractor")
        
        insert_data = {
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "contractor_name": contractor_name,
            "file_name": file_name,
            "total_amount": total,
            "boq_data": boq_data,
            "status": "pending"
        }
        
        res = supabase_admin.table("quotes").insert(insert_data).execute()
        
        if not res.data or len(res.data) == 0:
            return error(message="Failed to create quote", status_code=500)
        
        quote = res.data[0]
        
        # Send a message to the client
        from crud.messages import send_message
        contractor_name = current_user.get("user_metadata", {}).get("full_name", "Contractor")
        message_content = f"📋 New Quote from {contractor_name}\n\nFile: {file_name or 'Floor Plan'}\nTotal: ${total or 0:,.2f}\n\nCheck your quotes section to view details."
        send_message(sender_id, receiver_id, message_content, quote_id=quote["id"])
        
        logger.info(f"Quote sent from {sender_id} to {receiver_id}")
        return success(data=quote, message="Quote sent to client")
    except Exception as e:
        logger.error(f"Error sending quote: {e}")
        return error(message=str(e), status_code=500)


@router.get("/received/")
def get_received_quotes(current_user = Depends(get_current_user)):
    """Get all quotes received by the homeowner"""
    try:
        # Handle both dict and object types for user_id
        user_id = current_user["id"] if isinstance(current_user, dict) else current_user.id
        
        import logging
        logger = logging.getLogger("domnak")
        logger.info(f"get_received_quotes: user_id={user_id}")
        
        result = supabase_admin.table("quotes").select("*").eq("receiver_id", user_id).order("created_at", desc=True).execute()
        
        # Transform quotes - add sender_name and total field for frontend compatibility
        for quote in result.data:
            # Map total_amount to total for frontend
            quote["total"] = quote.get("total_amount", 0)
            quote["sender_name"] = "Architect"
        
        # Try to get sender names from profiles (non-blocking)
        sender_ids = list(set(q.get("sender_id") for q in result.data if q.get("sender_id")))
        if sender_ids:
            try:
                profiles = supabase_admin.table("profiles").select("id, full_name").in_("id", sender_ids).execute()
                sender_map = {p["id"]: p.get("full_name", "Architect") for p in (profiles.data or [])}
                for quote in result.data:
                    sender_id = quote.get("sender_id")
                    if sender_id in sender_map:
                        quote["sender_name"] = sender_map[sender_id]
            except Exception as profile_err:
                logger.warning(f"Could not fetch profiles: {profile_err}")
        
        return success(data=result.data)
    except Exception as e:
        import traceback
        logger = logging.getLogger("domnak")
        logger.error(f"Error in get_received_quotes: {str(e)}\n{traceback.format_exc()}")
        return error(message=str(e), status_code=500)

from db.supabase import supabase, supabase_admin
from datetime import datetime

def create_quote(user_id, contractor_name, total_amount, client_id=None):
    data = {
        "user_id": user_id,
        "contractor_name": contractor_name,
        "total_amount": total_amount,
        "status": "pending",
        "quality_tier": "standard",
        "created_at": datetime.now().isoformat()
    }
    if client_id:
        data["client_id"] = client_id
    result = supabase_admin.table("quotes").insert(data).execute()
    
    # Return the first item from data array
    if result.data and len(result.data) > 0:
        return result.data[0]
    return None

def get_quote(user_id):
    result = supabase.table("quotes").select("*").eq("user_id", user_id).execute()
    return result.data if result.data else []

def update_quote(quote_id, user_id, contractor_name, total_amount):
    data = {
        "contractor_name": contractor_name,
        "total_amount": total_amount,
        "updated_at": datetime.now().isoformat()
    }
    result = supabase_admin.table("quotes").update(data).eq("id", quote_id).eq("user_id", user_id).execute()
    if result.data and len(result.data) > 0:
        return result.data[0]
    return None

def delete_quote(quote_id, user_id):
    result = supabase_admin.table("quotes").delete().eq("id", quote_id).eq("user_id", user_id).execute()
    if result.data and len(result.data) > 0:
        return result.data[0]
    return None

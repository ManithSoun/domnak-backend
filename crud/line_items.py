from db.supabase import supabase
from datetime import datetime

def create_line_item(quote_id, material_name, quantity, unit, unit_price, total_price):
    data = {
        "quote_id": quote_id,
        "material_name": material_name,
        "quantity": quantity,
        "unit": unit,
        "unit_price": unit_price,
        "total_price": total_price,
        "created_at": datetime.now().isoformat()
    }
    result = supabase.table("line_items").insert(data).execute()
    return result.data[0] if result.data else None

def get_line_items(quote_id):
    result = supabase.table("line_items").select("*").eq("quote_id", quote_id).execute()
    return result.data if result.data else []

def update_line_item(item_id, material_name, quantity, unit, unit_price, total_price):
    data = {
        "material_name": material_name,
        "quantity": quantity,
        "unit": unit,
        "unit_price": unit_price,
        "total_price": total_price,
        "updated_at": datetime.now().isoformat()
    }
    result = supabase.table("line_items").update(data).eq("id", item_id).execute()
    return result.data[0] if result.data else None

def delete_line_item(item_id):
    result = supabase.table("line_items").delete().eq("id", item_id).execute()
    return result.data[0] if result.data else None

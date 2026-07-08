from db.supabase import supabase
from datetime import datetime

def save_analysis(quote_id, analysis_data, verdict):
    data = {
        "quote_id": quote_id,
        "analysis": analysis_data,
        "verdict": verdict,
        "created_at": datetime.now().isoformat()
    }
    result = supabase.table("analyses").insert(data).execute()
    return result.data[0] if result.data else None

def get_analysis(quote_id):
    result = supabase.table("analyses").select("*").eq("quote_id", quote_id).execute()
    return result.data[0] if result.data else None

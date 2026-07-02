from db.supabase import supabase

def save_analysis_result(quote_id: str, item_id: str, material: str, user_price: float, market_avg: float, verdict: str, reason: str):
    res = supabase.table("analysis_results").insert({
        "quote_id": quote_id,
        "item_id": item_id,
        "verdict": verdict,
        "explanation": reason,
        "market_price": market_avg,
        "overprice_percent": round(((user_price - market_avg) / market_avg) * 100, 1) if market_avg else 0,
        "negotiation_tip": None,
        "user_price": user_price,
        "market_avg": market_avg,
        "reason": reason
    }).execute()
    return res.data

def get_analysis_by_quote(quote_id: str):
    res = supabase.table("analysis_results").select("*").eq("quote_id", quote_id).execute()
    return res.data

def delete_analysis_by_quote(quote_id: str):
    res = supabase.table("analysis_results").delete().eq("quote_id", quote_id).execute()
    return res.data
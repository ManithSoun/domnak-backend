from db.supabase import supabase

def save_analysis_result(quote_id: str, item_id: str, material: str, user_price: float, market_avg: float, verdict: str, reason: str):
    # Fallback to user_price if market_avg is None/0 to satisfy DB NOT NULL constraint
    market_val = market_avg if (market_avg is not None and market_avg > 0) else user_price
    
    res = supabase.table("analysis_results").insert({
        "quote_id": quote_id,
        "item_id": item_id,
        "verdict": verdict,
        "explanation": reason,
        "market_price": market_val,
        "overprice_percent": round(((user_price - market_val) / market_val) * 100, 1) if market_val else 0,
        "negotiation_tip": None,
        "user_price": user_price,
        "market_avg": market_val,
        "reason": reason
    }).execute()
    return res.data

def get_analysis_by_quote(quote_id: str):
    res = supabase.table("analysis_results").select("*").eq("quote_id", quote_id).execute()
    return res.data

def delete_analysis_by_quote(quote_id: str):
    res = supabase.table("analysis_results").delete().eq("quote_id", quote_id).execute()
    return res.data
from db.supabase import supabase

def save_analysis_result(quote_id: str, item_id: str, verdict: str, explanation: str, market_price: float, overprice_percent: float, negotiation_tip: str):
  res = supabase.table("analysis_results").insert({
    "quote_id": quote_id,
    "item_id": item_id,
    "verdict": verdict,
    "explanation": explanation,
    "market_price": market_price,
    "overprice_percent": overprice_percent,
    "negotiation_tip": negotiation_tip
  }).execute()
  
  return res.data

def get_analysis_by_quote(quote_id: str):
  res = supabase.table("analysis_results").select("*").eq("quote_id", quote_id).execute()
  return res.data

def delete_analysis_by_quote(quote_id: str):
  res = supabase.table("analysis_results").delete().eq("quote_id", quote_id).execute()
  return res.data
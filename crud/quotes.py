from db.supabase import supabase

def create_quote(user_id: str, contractor_name: str, total_amount: float):
  res = supabase.table("quotes").insert({
    "user_id": user_id,
    "contractor_name": contractor_name,
    "total_amount": total_amount
  }).execute()
  return res.data

def get_quote(user_id: str):
  res = supabase.table("quotes").select("*").eq("user_id", user_id).execute()
  return res.data

def delete_quote(quote_id: str, user_id: str):
  res = supabase.table("quotes").delete().eq("id", quote_id).eq("user_id", user_id).execute()
  return res.data
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

def update_quote(quote_id: str, user_id: str, contractor_name: str = None, total_amount: float = None):
  updates = {}
  if contractor_name is not None:
    updates["contractor_name"] = contractor_name
  if total_amount is not None:
    updates["total_amount"] = total_amount
  res = supabase.table("quotes").update(updates).eq("id", quote_id).eq("user_id", user_id).execute()
  return res.data
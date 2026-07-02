from db.supabase import supabase

def create_line_item(quote_id: str, material_name: str, quantity: float, unit: str, unit_price: float, total_price: float = None):
  final_total = total_price if total_price is not None else round(quantity * unit_price, 2)
  
  res = supabase.table("line_items").insert({
    "quote_id": quote_id,
    "material_name": material_name,
    "quantity": quantity,
    "unit": unit,
    "unit_price": unit_price,
    "total_price": final_total
  }).execute()
  return res.data

def get_line_items(quote_id: str):
  res = supabase.table("line_items").select("*").eq("quote_id", quote_id).execute()
  return res.data

def delete_line_item(item_id: str):
  res = supabase.table("line_items").delete().eq("id", item_id).execute()
  return res.data

def update_line_item(item_id: str, material_name: str = None, quantity: float = None, unit: str = None, unit_price: float = None, total_price: float = None):
  updates = {}
  if material_name is not None:
    updates["material_name"] = material_name
  if quantity is not None:
    updates["quantity"] = quantity
  if unit is not None:
    updates["unit"] = unit
  if unit_price is not None:
    updates["unit_price"] = unit_price
  if total_price is not None:
    updates["total_price"] = total_price
  elif quantity is not None or unit_price is not None:
    final_total = total_price if total_price is not None else round(quantity * unit_price, 2)
    updates["total_price"] = final_total
  
  res = supabase.table("line_item").update(updates).eq("id", item_id).execute()
  return res.data
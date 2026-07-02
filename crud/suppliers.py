from db.supabase import supabase

def create_supplier( full_name: str, material_name: str, location: str, phone_number: str, price_per_unit: float, unit: str ):
  res = supabase.table("suppliers").insert({
    "full_name": full_name,
    "material_name": material_name,
    "location": location,
    "phone_number": phone_number,
    "price_per_unit": price_per_unit,
    "unit": unit
  }).execute()
  return res.data
  
def get_all_supplier():
  res = supabase.table("suppliers").select("*").execute()
  return res.data

def get_suppliers_by_material(material_name: str):
    res = supabase.table("suppliers").select("*").eq("material_name", material_name).execute()
    return res.data

def delete_supplier(supplier_id: str):
  res = supabase.table("suppliers").delete().eq("id", supplier_id).execute()
  return res.data

def update_supplier(supplier_id: str, full_name: str = None, material_name: str = None, location: str = None, phone_number: str = None, price_per_unit: float = None, unit: str = None):
  updates = {}
  if full_name is not None:
    updates["full_name"] = full_name
  if material_name is not None:
    updates["material_name"] = material_name
  if location is not None:
    updates["location"] = location
  if phone_number is not None:
    updates["phone_number"] = phone_number
  if price_per_unit is not None:
    updates["price_per_unit"] = price_per_unit
  if unit is not None:
    updates["unit"] = unit
  
  res = supabase.table("suppliers").update(updates).eq("id", supplier_id).execute()
  return res.data 

def track_click(supplier_id: str, user_id: str):
    res = supabase.table("referral_clicks").insert({
        "supplier_id": supplier_id,
        "user_id": user_id
    }).execute()
    return res.data

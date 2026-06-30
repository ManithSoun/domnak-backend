from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from db.supabase import supabase
from models.suppliers import SupplierRequest
from core.auth import get_current_user, get_admin_user
from typing import Optional


router = APIRouter()
security = HTTPBearer()

@router.get("/")
def get_suppliers():
  res = supabase.table("suppliers").select("*").execute()
  return res.data

@router.get("/{material_name}")
def get_suppliers_by_material(material_name: str):
  res = supabase.table("suppliers").select("*").eq("material_name", material_name).execute()
  return res.data

# access by admin only
@router.post("/")
def create_supplier(data: SupplierRequest, admin = Depends(get_admin_user), token: str = Depends(security)):
  res = supabase.table("suppliers").insert({
    "name": data.name,
    "material_name": data.material_name,
    "location": data.location,
    "phone": data.phone,
    "price_per_unit": data.price_per_unit,
    "unit": data.unit
  }).execute()
  return res.data

# referral click
@router.post("/{supplier_id}/click")
def track_click(supplier_id: str, current_user = Depends(get_current_user)):
  res = supabase.table("referral_clicks").insert({
    "supplier_id": supplier_id,
    "user_id": current_user.id
  }).execute()
  return {"message": "Click tracked"}

@router.patch("/{supplier_id}")
def update_supplier(supplier_id: str, data: SupplierRequest, admin = Depends(get_admin_user)):
    res = supabase.table("suppliers").update({
        "price_per_unit": data.price_per_unit
    }).eq("id", supplier_id).execute()
    return res.data

# Admin only
@router.delete("/{supplier_id}")
def delete_supplier(supplier_id: str, admin = Depends(get_admin_user)):
    supabase.table("suppliers").delete().eq("id", supplier_id).execute()
    return {"message": "Supplier deleted"}
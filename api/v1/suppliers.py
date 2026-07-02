from fastapi import APIRouter, Depends
from models.suppliers import SupplierRequest, SupplierUpdateRequest
from core.auth import get_current_user, get_admin_user
from core.logging import logger
import crud.suppliers as supplier_crud
from utils.response import success, error

router = APIRouter()

@router.get("/")
def get_suppliers():
    try:
        result = supplier_crud.get_all_supplier()
        logger.info("Fetched all suppliers")
        return success(data=result)
    except Exception as e:
        logger.error(f"Failed to fetch suppliers: {str(e)}")
        return error(message=str(e), status_code=500)

@router.get("/{material_name}")
def get_suppliers_by_material(material_name: str):
    try:
        result = supplier_crud.get_suppliers_by_material(material_name)
        logger.info(f"Fetched suppliers for material: {material_name}")
        return success(data=result)
    except Exception as e:
        logger.error(f"Failed to fetch suppliers by material: {str(e)}")
        return error(message=str(e), status_code=500)

@router.post("/")
def create_supplier(data: SupplierRequest, admin = Depends(get_admin_user)):
    try:
        result = supplier_crud.create_supplier(
            data.full_name,
            data.material_name,
            data.location,
            data.phone_number,
            data.price_per_unit,
            data.unit
        )
        logger.info(f"Admin {admin.id} created supplier: {data.full_name}")
        return success(data=result, message=f"Supplier created by admin {admin.id}")
    except Exception as e:
        logger.error(f"Admin {admin.id} failed to create supplier: {str(e)}")
        return error(message=str(e), status_code=500)

@router.post("/{supplier_id}/click")
def track_click(supplier_id: str, current_user = Depends(get_current_user)):
    try:
        supplier_crud.track_click(supplier_id, current_user.id)
        logger.info(f"User {current_user.id} clicked supplier {supplier_id}")
        return success(message="Click tracked")
    except Exception as e:
        logger.error(f"Failed to track click: {str(e)}")
        return error(message=str(e), status_code=500)

@router.patch("/{supplier_id}")
def update_supplier(supplier_id: str, data: SupplierUpdateRequest, admin = Depends(get_admin_user)):
    try:
        result = supplier_crud.update_supplier(
            supplier_id,
            data.full_name,
            data.material_name,
            data.location,
            data.phone_number,
            data.price_per_unit,
            data.unit
        )
        logger.info(f"Admin {admin.id} updated supplier {supplier_id}")
        return success(data=result)
    except Exception as e:
        logger.error(f"Admin {admin.id} failed to update supplier {supplier_id}: {str(e)}")
        return error(message=str(e), status_code=500)

@router.delete("/{supplier_id}")
def delete_supplier(supplier_id: str, admin = Depends(get_admin_user)):
    try:
        supplier_crud.delete_supplier(supplier_id)
        logger.info(f"Admin {admin.id} deleted supplier {supplier_id}")
        return success(message="Supplier deleted")
    except Exception as e:
        logger.error(f"Admin {admin.id} failed to delete supplier {supplier_id}: {str(e)}")
        return error(message=str(e), status_code=500)
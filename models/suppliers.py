from pydantic import BaseModel, field_validator
import phonenumbers
from phonenumbers import NumberParseException
from typing import Optional

class BaseSupplierRequest(BaseModel):

    @field_validator('full_name', mode='before')
    @classmethod
    def validate_full_name(cls, value):
        if value is None:
            return value
        if len(value) < 3:
            raise ValueError('Name must be at least 3 characters')
        if len(value) > 100:
            raise ValueError('Name must be less than 100 characters')
        return value

    @field_validator('material_name', mode='before')
    @classmethod
    def validate_material_name(cls, value):
        if value is None:
            return value
        if len(value) < 2:
            raise ValueError('Material name must be at least 2 characters')
        return value

    @field_validator('location', mode='before')
    @classmethod
    def validate_location(cls, value):
        if value is None:
            return value
        if len(value) < 3:
            raise ValueError('Location must be at least 3 characters')
        return value

    @field_validator('phone_number', mode='before')
    @classmethod
    def validate_phone(cls, value):
        if value is None:
            return value
        try:
            parsed = phonenumbers.parse(value, "KH")
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError("Invalid phone number")
            return value
        except NumberParseException:
            raise ValueError("Phone number format is invalid. Example: 012345678 or +85512345678")

    @field_validator('price_per_unit', mode='before')
    @classmethod
    def validate_price(cls, value):
        if value is None:
            return value
        if value <= 0:
            raise ValueError("Price must be greater than 0")
        return value

    @field_validator('unit', mode='before')
    @classmethod
    def validate_unit(cls, value):
        if value is None:
            return value
        valid_units = ['bag', 'm²', 'm³', 'ton', 'meter', 'liter', 'set', 'roll', 'kg', 'pcs', 'bf']
        if value not in valid_units:
            raise ValueError(f"Unit must be one of: {', '.join(valid_units)}")
        return value


class SupplierRequest(BaseSupplierRequest):
    full_name: str
    material_name: str
    location: str
    phone_number: str
    price_per_unit: float
    unit: str


class SupplierUpdateRequest(BaseSupplierRequest):
    full_name: Optional[str] = None
    material_name: Optional[str] = None
    location: Optional[str] = None
    phone_number: Optional[str] = None
    price_per_unit: Optional[float] = None
    unit: Optional[str] = None
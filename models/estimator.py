from pydantic import BaseModel, field_validator
from db.supabase import supabase

class EstimatorRequest(BaseModel):
    floor_area: float
    storeys: int
    finishing: str
    roof_type: str
    location: str

    @field_validator('floor_area')
    @classmethod
    def validate_floor_area(cls, value):
        if value <= 0:
            raise ValueError("Floor area must be greater than 0")
        if value > 10000:
            raise ValueError("Floor area seems too large — max 10,000 m²")
        return value

    @field_validator('storeys')
    @classmethod
    def validate_storeys(cls, value):
        if value not in [1, 2]:
            raise ValueError("Storeys must be 1 or 2")
        return value

    @field_validator('finishing')
    @classmethod
    def validate_finishing(cls, value):
        if value not in ['basic', 'standard', 'premium']:
            raise ValueError("Finishing must be 'basic', 'standard', or 'premium'")
        return value

    @field_validator('roof_type')
    @classmethod
    def validate_roof_type(cls, value):
        if value not in ['flat', 'pitched', 'metal']:
            raise ValueError("Roof type must be 'flat', 'pitched', or 'metal'")
        return value

    @field_validator('location')
    @classmethod
    def validate_location(cls, value):
        if value not in ['phnom_penh', 'province']:
            raise ValueError("Location must be 'phnom_penh' or 'province'")
        return value
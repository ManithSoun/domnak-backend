import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.supabase import supabase
from dotenv import load_dotenv

load_dotenv()

suppliers = [
    {"name": "Chip Mong Construction", "material_name": "Cement", "location": "Sen Sok, Phnom Penh", "phone": "023-123-456", "price_per_unit": 6.80, "unit": "bag"},
    {"name": "Lucky Building Materials", "material_name": "Cement", "location": "Toul Kork, Phnom Penh", "phone": "023-234-567", "price_per_unit": 7.10, "unit": "bag"},
    {"name": "Bayon Hardware", "material_name": "Cement", "location": "Meanchey, Phnom Penh", "phone": "023-345-678", "price_per_unit": 7.25, "unit": "bag"},
    {"name": "Chip Mong Construction", "material_name": "Rebar", "location": "Sen Sok, Phnom Penh", "phone": "023-123-456", "price_per_unit": 840.00, "unit": "ton"},
    {"name": "Lucky Building Materials", "material_name": "Rebar", "location": "Toul Kork, Phnom Penh", "phone": "023-234-567", "price_per_unit": 860.00, "unit": "ton"},
    {"name": "Bayon Hardware", "material_name": "Sand", "location": "Meanchey, Phnom Penh", "phone": "023-345-678", "price_per_unit": 24.00, "unit": "m³"},
    {"name": "Phnom Penh Building Supply", "material_name": "Sand", "location": "Chamkarmon, Phnom Penh", "phone": "023-456-789", "price_per_unit": 26.00, "unit": "m³"},
    {"name": "Chip Mong Construction", "material_name": "Gravel", "location": "Sen Sok, Phnom Penh", "phone": "023-123-456", "price_per_unit": 26.00, "unit": "m³"},
    {"name": "Lucky Building Materials", "material_name": "Gravel", "location": "Toul Kork, Phnom Penh", "phone": "023-234-567", "price_per_unit": 28.00, "unit": "m³"},
    {"name": "Bayon Hardware", "material_name": "Ceramic tile", "location": "Meanchey, Phnom Penh", "phone": "023-345-678", "price_per_unit": 6.50, "unit": "m²"},
    {"name": "Phnom Penh Building Supply", "material_name": "Ceramic tile", "location": "Chamkarmon, Phnom Penh", "phone": "023-456-789", "price_per_unit": 7.00, "unit": "m²"},
    {"name": "Chip Mong Construction", "material_name": "Brick", "location": "Sen Sok, Phnom Penh", "phone": "023-123-456", "price_per_unit": 0.085, "unit": "pcs"},
    {"name": "Lucky Building Materials", "material_name": "PVC pipe", "location": "Toul Kork, Phnom Penh", "phone": "023-234-567", "price_per_unit": 2.50, "unit": "meter"},
    {"name": "Bayon Hardware", "material_name": "Electrical wire", "location": "Meanchey, Phnom Penh", "phone": "023-345-678", "price_per_unit": 0.75, "unit": "meter"},
]
res = supabase.table("suppliers").insert(suppliers).execute()
print(f"Inserted {len(res.data)} suppliers")
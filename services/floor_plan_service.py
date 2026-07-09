import os
import re
import json
import base64
from PIL import Image
import pytesseract
from groq import Groq
from dotenv import load_dotenv
import io

load_dotenv()

class FloorPlanService:
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"
    
    def extract_text_from_image(self, image_bytes):
        """Extract text from image using Tesseract OCR"""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""
    
    def extract_dimensions(self, text):
        """Extract room dimensions from OCR text using regex"""
        dim_pattern = re.compile(r'(\d+\.?\d*)\s*[x×]\s*(\d+\.?\d*)')
        dims = dim_pattern.findall(text)
        
        room_names = ['Living Room', 'Kitchen', 'Bedroom 1', 'Bedroom 2', 'Bathroom', 'Dining Room']
        rooms = []
        
        for i, (w, l) in enumerate(dims[:6]):
            try:
                width = float(w)
                length = float(l)
                area = round(width * length, 2)
                rooms.append({
                    "name": room_names[i] if i < len(room_names) else f"Room {i+1}",
                    "width": width,
                    "length": length,
                    "area": area
                })
            except:
                continue
        
        return rooms
    
    def analyze_with_groq(self, extracted_text, rooms):
        """Use Groq AI to structure the floor plan data"""
        prompt = f"""
        You are an expert architectural parser. Analyze this floor plan data and return structured JSON.
        
        Raw OCR text:
        {extracted_text[:500]}
        
        Extracted dimensions:
        {json.dumps(rooms, indent=2)}
        
        Return ONLY valid JSON with:
        {{
            "rooms": [
                {{"name": "Living Room", "width": 5.0, "length": 6.0, "area": 30.0}}
            ],
            "total_area": 81.5,
            "building_type": "residential",
            "floors": 1,
            "features": ["balcony", "garden"]
        }}
        
        If rooms are empty, use reasonable estimates for a 2-bedroom house.
        """
        
        try:
            completion = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            return json.loads(completion.choices[0].message.content)
        except Exception as e:
            print(f"Groq analysis error: {e}")
            return {
                "rooms": rooms if rooms else [
                    {"name": "Living Room", "width": 5.0, "length": 6.0, "area": 30.0},
                    {"name": "Kitchen", "width": 4.0, "length": 3.5, "area": 14.0},
                    {"name": "Bedroom 1", "width": 4.0, "length": 4.0, "area": 16.0},
                    {"name": "Bedroom 2", "width": 3.5, "length": 4.0, "area": 14.0},
                    {"name": "Bathroom", "width": 3.0, "length": 2.5, "area": 7.5}
                ],
                "total_area": 81.5,
                "building_type": "residential",
                "floors": 1,
                "features": []
            }
    
    def calculate_boq(self, analysis):
        """Calculate BOQ from floor plan analysis"""
        total_area = analysis.get("total_area", 0)
        
        if total_area <= 0:
            return {"error": "Invalid area"}
        
        # Cambodia construction rates (per m²)
        rates = {
            "cement_bags": {"rate": 3.5, "price": 8.50, "unit": "bag"},
            "steel_kg": {"rate": 40.0, "price": 0.85, "unit": "kg"},
            "bricks": {"rate": 320.0, "price": 0.08, "unit": "pcs"},
            "sand_cubic_meters": {"rate": 0.25, "price": 45.0, "unit": "m³"},
            "gravel_cubic_meters": {"rate": 0.20, "price": 40.0, "unit": "m³"},
            "paint_liters": {"rate": 0.8, "price": 12.0, "unit": "liter"},
            "tiles_sqm": {"rate": 1.0, "price": 15.0, "unit": "m²"},
            "electrical_wire_m": {"rate": 8.0, "price": 2.5, "unit": "meter"},
            "pvc_pipes_m": {"rate": 1.0, "price": 3.0, "unit": "meter"}
        }
        
        quantities = {}
        cost_breakdown = {}
        
        for material, data in rates.items():
            qty = round(total_area * data["rate"], 2)
            cost = round(qty * data["price"], 2)
            quantities[material] = {
                "quantity": qty,
                "unit": data["unit"],
                "price_per_unit": data["price"],
                "total_cost": cost
            }
            cost_breakdown[material] = cost
        
        total_material_cost = round(sum(cost_breakdown.values()), 2)
        labor_cost = round(total_area * 65.0, 2)
        structural_markup = round(total_material_cost * 0.15, 2)
        total_cost = round(total_material_cost + labor_cost + structural_markup, 2)
        
        return {
            "quantities": quantities,
            "cost_breakdown": cost_breakdown,
            "labor_cost": labor_cost,
            "structural_markup": structural_markup,
            "total_material_cost": total_material_cost,
            "total_estimated_cost": total_cost,
            "cost_per_sqm": round(total_cost / total_area, 2) if total_area > 0 else 0
        }
    
    def process_floor_plan(self, image_bytes):
        """Complete floor plan processing pipeline"""
        # Step 1: OCR
        extracted_text = self.extract_text_from_image(image_bytes)
        
        # Step 2: Extract dimensions
        rooms = self.extract_dimensions(extracted_text)
        
        # Step 3: AI analysis
        analysis = self.analyze_with_groq(extracted_text, rooms)
        
        # Step 4: Calculate BOQ
        boq = self.calculate_boq(analysis)
        
        return {
            "analysis": analysis,
            "boq": boq,
            "extracted_text": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
            "rooms_count": len(analysis.get("rooms", [])),
            "total_area": analysis.get("total_area", 0)
        }

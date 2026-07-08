# services/groq_service.py
import os
import json
from groq import Groq
from typing import List, Dict, Any
from models.analyze import AnalysisResult

class GroqService:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.1-70b-versatile"  # or "mixtral-8x7b-32768"
    
    def analyze_quote(self, line_items: List[Dict]) -> List[Dict]:
        """Analyze quote line items and return structured analysis"""
        
        prompt = self._build_analysis_prompt(line_items)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": """You are a construction cost estimator AI assistant.
                    Analyze construction materials and compare them to Cambodian market rates.
                    Return ONLY valid JSON with no additional text.
                    The JSON should be an array of objects with these fields:
                    - material_name: string
                    - quantity: number
                    - unit: string
                    - quoted_price: number
                    - market_price: number
                    - verdict: "fair" | "slightly_high" | "overpriced"
                    - overprice_percent: number
                    - explanation: string
                    - negotiation_tip: string (optional)"""
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=4096,
            response_format={"type": "json_object"}
        )
        
        return self._parse_response(response.choices[0].message.content)
    
    def _build_analysis_prompt(self, line_items: List[Dict]) -> str:
        """Build the prompt with market rate data"""
        
        # Market rates database (Cambodia construction materials)
        MARKET_RATES = {
            "cement": {"price": 6.50, "unit": "bag"},
            "sand": {"price": 45.00, "unit": "m³"},
            "gravel": {"price": 50.00, "unit": "m³"},
            "steel": {"price": 1.20, "unit": "kg"},
            "rebar": {"price": 1.20, "unit": "kg"},
            "brick": {"price": 0.25, "unit": "pcs"},
            "paint": {"price": 3.80, "unit": "liter"},
            "tiles": {"price": 12.00, "unit": "m²"},
            "wood": {"price": 8.50, "unit": "meter"},
            "electrical_wire": {"price": 15.00, "unit": "meter"},
            "pvc_pipe": {"price": 2.50, "unit": "meter"},
            "labor": {"price": 25.00, "unit": "hour"},
        }
        
        prompt = """
        Analyze these construction materials and compare to CAMBODIAN MARKET RATES.
        
        MARKET RATES (USD per unit, Phnom Penh prices):
        """
        for material, data in MARKET_RATES.items():
            prompt += f"\n- {material.title()}: ${data['price']} per {data['unit']}"
        
        prompt += "\n\nUSER'S QUOTE LINE ITEMS:\n"
        for item in line_items:
            prompt += f"- {item.get('material_name', 'Unknown')}: {item.get('quantity', 0)} {item.get('unit', 'units')} @ ${item.get('unit_price', 0)} each\n"
        
        prompt += """
        
        RULES:
        1. If quoted price is within 5% of market rate → verdict = "fair"
        2. If quoted price is 5-20% above market → verdict = "slightly_high"
        3. If quoted price is over 20% above market → verdict = "overpriced"
        4. For materials not in the market rate list, use your construction knowledge
        5. For labor, compare to standard Cambodian rates ($25-35/hour for skilled labor)
        6. Provide specific negotiation tips in Cambodian context
        
        Return the analysis as a JSON array.
        """
        return prompt
    
    def _parse_response(self, response_text: str) -> List[Dict]:
        """Parse and validate the AI response"""
        try:
            # Clean the response (remove markdown code blocks if present)
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            data = json.loads(cleaned)
            
            # Handle both object and array responses
            if isinstance(data, dict):
                if "results" in data:
                    return data["results"]
                elif "analysis" in data:
                    return data["analysis"]
                # If it's a single object, wrap in array
                if "material_name" in data:
                    return [data]
            elif isinstance(data, list):
                return data
            
            return []
        except json.JSONDecodeError as e:
            print(f"Failed to parse AI response: {e}")
            return []
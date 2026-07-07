import os
from groq import Groq
import json
from typing import List, Dict
from models.analyze import AnalysisResult

class AIService:
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    def analyze_quote(self, line_items: List[Dict]) -> List[AnalysisResult]:
        """Send quote to Groq and get structured analysis"""
        prompt = self._build_analysis_prompt(line_items)
        
        response = self.groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a construction cost estimator AI..."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        return self._parse_response(response.choices[0].message.content)
    
    def _build_analysis_prompt(self, line_items):
        prompt = """
        Analyze these construction materials and compare to market rates.
        For each item, provide:
        - verdict: "fair" if within 5% of market, "slightly_high" if 5-20% over, "overpriced" if over 20%
        - overprice_percent: percentage over market
        - explanation: brief reason
        - negotiation_tip: actionable advice
        
        Market rates (USD per unit):
        - Cement (bag): $6.50
        - Sand (m³): $45.00
        - Steel (kg): $1.20
        - Brick (pcs): $0.25
        - Paint (liter): $3.80
        
        User quote:
        """
        for item in line_items:
            prompt += f"\n- {item['material_name']}: {item['quantity']} {item['unit']} @ ${item['unit_price']}"
        return prompt
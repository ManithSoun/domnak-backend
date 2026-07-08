# services/groq_agent.py
class GroqAgent:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    def detect_red_flags(self, quote_data: dict) -> dict:
        """Detect red flags and generate warnings"""
        
        # Compare with benchmarks
        benchmarks = self._get_benchmarks()
        line_items = quote_data.get("line_items", [])
        
        red_flags = []
        for item in line_items:
            market_price = benchmarks.get(item.get("material_name", ""), {}).get("price", 0)
            if market_price > 0:
                quoted = item.get("unit_price", 0)
                percent_over = ((quoted - market_price) / market_price) * 100
                
                if percent_over > 20:
                    red_flags.append({
                        "item": item.get("material_name"),
                        "severity": "high" if percent_over > 50 else "medium",
                        "message": f"{item.get('material_name')} is {percent_over:.0f}% above market rate",
                        "savings": (quoted - market_price) * item.get("quantity", 1)
                    })
        
        # Get AI-generated warnings
        prompt = self._build_warning_prompt(quote_data, red_flags)
        response = self.client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a construction cost auditor. Identify red flags and provide warnings."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        return {
            "red_flags": red_flags,
            "ai_insights": response.choices[0].message.content,
            "total_potential_savings": sum(r["savings"] for r in red_flags)
        }
    
    def _get_benchmarks(self) -> dict:
        """Return benchmark data for common materials"""
        return {
            "cement": {"price": 6.50, "unit": "bag"},
            "sand": {"price": 45.00, "unit": "m³"},
            "steel": {"price": 1.20, "unit": "kg"},
            "brick": {"price": 0.25, "unit": "pcs"},
            "paint": {"price": 3.80, "unit": "liter"},
            "tiles": {"price": 12.00, "unit": "m²"},
            # ... more materials
        }
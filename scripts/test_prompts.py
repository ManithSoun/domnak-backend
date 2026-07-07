# scripts/test_prompts.py
import json
from services.groq_service import GroqService

def test_prompt_tuning():
    """Test and tune prompts with sample data"""
    
    groq = GroqService()
    
    # Sample test quotes
    test_cases = [
        {
            "name": "Fair quote",
            "items": [
                {"material_name": "cement", "quantity": 50, "unit": "bag", "unit_price": 6.80},
                {"material_name": "sand", "quantity": 5, "unit": "m³", "unit_price": 48.00}
            ]
        },
        {
            "name": "Overpriced quote",
            "items": [
                {"material_name": "cement", "quantity": 50, "unit": "bag", "unit_price": 9.00},
                {"material_name": "steel", "quantity": 100, "unit": "kg", "unit_price": 1.80}
            ]
        }
    ]
    
    results = []
    for test in test_cases:
        print(f"\nTesting: {test['name']}")
        result = groq.analyze_quote(test['items'])
        results.append({
            "test_name": test['name'],
            "result": result
        })
    
    # Save results for evaluation
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    test_prompt_tuning()
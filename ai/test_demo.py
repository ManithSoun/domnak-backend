import json
from analyze_quote import analyze_quote
from reference_data import load_reference_prices

ref = load_reference_prices()
with open('demo_quote.json') as f:
    data = json.load(f)
result = analyze_quote(data['line_items'], ref)
print(json.dumps(result, indent=2))

import json
import os
from analyze_quote import analyze_quote
from reference_data import load_reference_prices

ref = load_reference_prices()

for filename in sorted(os.listdir("test_quotes")):
    if filename.endswith(".json"):
        with open(f"test_quotes/{filename}") as f:
            data = json.load(f)
            quote = data["line_items"]
        print(f"\n=== {filename} ===")
        result = analyze_quote(quote, ref)
        print(json.dumps(result, indent=2))
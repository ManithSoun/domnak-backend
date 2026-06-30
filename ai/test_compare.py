import json
from compare_quotes import compare_quotes

quote1 = [
    {"material": "cement", "quantity": 100, "unit": "bag", "unit_price": 5.20},
    {"material": "steel bar", "quantity": 200, "unit": "kg", "unit_price": 1.25},
]
quote2 = [
    {"material": "cement", "quantity": 100, "unit": "bag", "unit_price": 7.00},
    {"material": "steel bar", "quantity": 200, "unit": "kg", "unit_price": 1.80},
]
summary = compare_quotes([quote1, quote2])
print(json.dumps(summary, indent=2))

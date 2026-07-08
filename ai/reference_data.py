import json

def load_reference_prices():
    with open("materials.json", "r") as f:
        return json.load(f)

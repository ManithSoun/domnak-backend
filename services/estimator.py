rates = {
    "1": {
        "basic":    {"min": 220, "max": 280},
        "standard": {"min": 300, "max": 380},
        "premium":  {"min": 420, "max": 550}
    },
    "2": {
        "basic":    {"min": 260, "max": 320},
        "standard": {"min": 340, "max": 420},
        "premium":  {"min": 460, "max": 600}
    }
}

location_multiplier = {
    "phnom_penh": 1.0,
    "province": 0.90
}

roof_adjustment = {
    "flat": 0,
    "pitched": 15,
    "metal": -10
}

def calculate_estimate(floor_area: float, storeys: int, finishing: str, roof_type: str, location: str):
    rate = rates[str(storeys)][finishing]
    multiplier = location_multiplier[location]
    roof_adj = roof_adjustment[roof_type]
    
    min_cost = round((floor_area * rate["min"] * multiplier) + (roof_adj * floor_area))
    max_cost = round((floor_area * rate["max"] * multiplier) + (roof_adj * floor_area))
    
    return {
        "min_cost": min_cost,
        "max_cost": max_cost,
        "floor_area": floor_area,
        "finishing": finishing,
        "location": location,
        "rate_per_m2": rate
    }
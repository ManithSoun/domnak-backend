import json
from analyze_quote import analyze_quote
from reference_data import load_reference_prices

def compare_quotes(quotes_list, ref=None):
    if ref is None:
        ref = load_reference_prices()
    
    results = []
    for idx, quote in enumerate(quotes_list):
        analysis = analyze_quote(quote, ref)
        total_user = 0
        total_market = 0
        for i, item in enumerate(analysis):
            if i < len(quote):
                qty = quote[i]["quantity"]
                total_user += item["user_price"] * qty
                if item.get("market_avg") is not None:
                    total_market += item["market_avg"] * qty
        deviation_pct = ((total_user - total_market) / total_market * 100) if total_market else None
        results.append({
            "quote_index": idx,
            "analysis": analysis,
            "total_user_price": total_user,
            "total_market_price": total_market,
            "deviation_percent": deviation_pct
        })
    
    best = min(results, key=lambda x: x["total_user_price"]) if results else None
    worst = max(results, key=lambda x: x["total_user_price"]) if results else None

    summary = {
        "quote_count": len(results),
        "best_quote": best,
        "worst_quote": worst,
        "details": results
    }
    return summary

import json
import os
import groq
from dotenv import load_dotenv
from reference_data import load_reference_prices

load_dotenv()
client = groq.Client(api_key=os.getenv("GROQ_API_KEY"))

def analyze_quote(line_items, ref_data):
    ref_text = "\n".join([f"- {item['material']}: {item['avg_price']} {item['unit']}" for item in ref_data])
    items_text = "\n".join([f"- {it['material']} | Qty: {it['quantity']} | Unit: {it['unit']} | Price: {it['unit_price']}" for it in line_items])
    prompt = f"""
You are a construction cost analyst. Compare each line item against the market reference prices.

REFERENCE PRICES (per unit):
{ref_text}

USER QUOTE:
{items_text}

Determine the overpricing status based ONLY on how much the user's price is above the market average.
- If the user's price is NOT overpriced (i.e., <= market_avg * 1.05), status = "green".
  This includes any price that is below or equal to market average, or only slightly above (within 5%).
- If the user's price is moderately overpriced (between 1.05 and 1.20 times market_avg), status = "amber".
- If the user's price is significantly overpriced (> 1.20 times market_avg), status = "red".
- If the material is not in the reference list, status = "unknown" and set market_avg = null.

Return a JSON array with objects:
{{
  "material": "string",
  "user_price": number,
  "market_avg": number or null,
  "status": "green" or "amber" or "red" or "unknown",
  "reason": "brief explanation"
}}
Return ONLY the JSON array. No extra text.
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )
    result_text = response.choices[0].message.content.strip()
    if result_text.startswith("```json"):
        result_text = result_text[7:]
    if result_text.endswith("```"):
        result_text = result_text[:-3]
    return json.loads(result_text)
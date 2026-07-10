from fastapi import APIRouter, Depends
from db.supabase import supabase
from core.auth import get_current_user
from core.logging import logger
from utils.response import success, error
import crud.analysis as analysis_crud
from groq import Groq
from config import settings
import json

router = APIRouter()
client = Groq(api_key=settings.groq_api_key)

with open("data/cambodia_prices.json") as f:
    price_data = json.load(f)

def build_ref_text():
    return "\n".join([
        f"- {m['material_name']}: {(m['price_min_usd'] + m['price_max_usd']) / 2} {m['unit']}"
        for m in price_data['materials']
    ])

@router.post("/{quote_id}")
def analysis_quote(quote_id: str, current_user = Depends(get_current_user)):
    try:
        print(f"DEBUG: current_user type = {type(current_user)}")
        print(f"DEBUG: current_user = {current_user}")
        print(f"DEBUG: quote_id = {quote_id}")
        # Step 1 — verify ownership
        quote = supabase.table("quotes").select("*").eq("id", quote_id).eq("user_id", current_user.id).single().execute()
        if not quote.data:
            return error(message="Quote not found or access denied", status_code=403)

        # Step 2 — fetch line items
        items = supabase.table("line_items").select("*").eq("quote_id", quote_id).execute()
        if not items.data:
            return error(message="No line items found — add items before analyzing", status_code=400)

        # Step 3 — delete old analysis if exists
        analysis_crud.delete_analysis_by_quote(quote_id)

        # Step 4 — build prompt
        ref_text = build_ref_text()
        items_text = "\n".join([
            f"- {item['material_name']} | Qty: {item['quantity']} | Unit: {item['unit']} | Price: {item['unit_price']}"
            for item in items.data
        ])

        prompt = f"""
You are a construction cost analyst. Compare each line item against the market reference prices.

REFERENCE PRICES (per unit):
{ref_text}

USER QUOTE:
{items_text}

Determine the overpricing status based ONLY on how much the user's price is above the market average.
- If the user's price is NOT overpriced (i.e., <= market_avg * 1.05), status = "green".
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

        # Step 5 — call Groq
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

        result_text = response.choices[0].message.content.strip()
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]

        analysis = json.loads(result_text)

        # Step 6 — save results
        for item_analysis in analysis:
            matching_item = next(
                (i for i in items.data if i['material_name'].lower() == item_analysis['material'].lower()),
                None
            )
            if matching_item:
                analysis_crud.save_analysis_result(
                    quote_id=quote_id,
                    item_id=matching_item['id'],
                    material=item_analysis['material'],
                    user_price=item_analysis['user_price'],
                    market_avg=item_analysis['market_avg'],
                    verdict=item_analysis['status'],
                    reason=item_analysis['reason']
                )

        # Step 7 — update quote status
        supabase.table("quotes").update({"status": "analyzed"}).eq("id", quote_id).execute()

        logger.info(f"Quote {quote_id} analyzed — {len(analysis)} items")
        return success(data={"quote_id": quote_id, "analysis": analysis})

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        return error(message=str(e), status_code=500)

@router.get("/{quote_id}")
def get_analysis(quote_id: str, current_user = Depends(get_current_user)):
    try:
        quote = supabase.table("quotes").select("id").eq("id", quote_id).eq("user_id", current_user.id).single().execute()
        if not quote.data:
            return error(message="Quote not found or access denied", status_code=403)

        result = analysis_crud.get_analysis_by_quote(quote_id)
        return success(data=result)
    except Exception as e:
        logger.error(f"Failed to fetch analysis: {str(e)}")
        return error(message=str(e), status_code=500)
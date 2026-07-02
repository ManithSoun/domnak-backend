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

# load price reference data
with open("data/cambodia_prices.json") as f:
    price_data = json.load(f)

@router.post("/{quote_id}")
def analyze_quote(quote_id: str, current_user = Depends(get_current_user)):
    try:
        # Step 1 — verify quote belongs to user
        quote = supabase.table("quotes").select("*").eq("id", quote_id).eq("user_id", current_user.id).single().execute()
        if not quote.data:
            return error(message="Quote not found or access denied", status_code=403)

        # Step 2 — fetch line items
        items = supabase.table("line_items").select("*").eq("quote_id", quote_id).execute()
        if not items.data:
            return error(message="No line items found — add items before analyzing", status_code=400)

        # Step 3 — format line items for prompt
        quote_items = "\n".join([
            f"- {item['material_name']}: {item['quantity']} {item['unit']} at ${item['unit_price']} per {item['unit']}, total ${item['total_price']}"
            for item in items.data
        ])

        # Step 4 — format price reference
        price_reference = "\n".join([
            f"- {m['material_name']}: fair range ${m['price_min_usd']} - ${m['price_max_usd']} per {m['unit']}"
            for m in price_data['materials']
        ])

        # Step 5 — send to Groq
        prompt = f"""You are a construction cost advisor in Cambodia.

Here is a homeowner's contractor quotation:
{quote_items}

Here are the fair market prices in Phnom Penh:
{price_reference}

Analyze each line item and return ONLY a JSON array. No other text, no markdown, no backticks.

Each object must have exactly these fields:
- material_name: string
- quantity: number
- unit: string
- quoted_price: number (the unit price quoted)
- market_price: number (fair market price per unit)
- verdict: exactly one of "fair", "overpriced", or "slightly_high"
- overprice_percent: number (0 if fair)
- explanation: string (simple language, max 2 sentences)
- negotiation_tip: string or null (one sentence advice, null if fair)
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        # Step 6 — parse response
        result = response.choices[0].message.content.strip()
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]

        analysis = json.loads(result)

        # Step 7 — save to analysis_results table
        for item_analysis in analysis:
            matching_item = next(
                (i for i in items.data if i['material_name'].lower() == item_analysis['material_name'].lower()),
                None
            )
            if matching_item:
                analysis_crud.save_analysis_result(
                    quote_id=quote_id,
                    item_id=matching_item['id'],
                    verdict=item_analysis['verdict'],
                    explanation=item_analysis['explanation'],
                    market_price=item_analysis['market_price'],
                    overprice_percent=item_analysis['overprice_percent'],
                    negotiation_tip=item_analysis['negotiation_tip']
                )

        # Step 8 — update quote status to analyzed
        supabase.table("quotes").update({"status": "analyzed"}).eq("id", quote_id).execute()

        logger.info(f"Quote {quote_id} analyzed — {len(analysis)} items processed")
        return success(data={"quote_id": quote_id, "analysis": analysis})

    except Exception as e:
        logger.error(f"Analysis failed for quote {quote_id}: {str(e)}")
        return error(message=str(e), status_code=500)

@router.get("/{quote_id}")
def get_analysis(quote_id: str, current_user = Depends(get_current_user)):
    try:
        # verify ownership
        quote = supabase.table("quotes").select("id").eq("id", quote_id).eq("user_id", current_user.id).single().execute()
        if not quote.data:
            return error(message="Quote not found or access denied", status_code=403)

        result = analysis_crud.get_analysis_by_quote(quote_id)
        return success(data=result)
    except Exception as e:
        logger.error(f"Failed to fetch analysis for quote {quote_id}: {str(e)}")
        return error(message=str(e), status_code=500)
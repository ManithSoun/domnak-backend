import fitz
import json
import base64
from groq import Groq
from config import settings

client = Groq(api_key=settings.groq_api_key)

def parse_pdf(file_bytes: bytes) -> list:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()

    use_vision = True
    line_items = []

    if text.strip() and len(text.strip()) > 50:
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a construction quote parser.
                        Extract all line items (including labor, services, and materials) from the quote text and return ONLY a JSON array.
                        Each item must have: material_name, quantity, unit, unit_price, total_price.
                        For total_price, extract the total cost of the line item (which includes both labor and material costs, typically under the 'Total Cost' or 'Amount' column). If the quote is broken down by Labour Cost and Materials Cost, use the combined 'Total Cost' for total_price.
                        If you cannot find a value, use null.
                        Return only the JSON array, no other text, no markdown, no backticks."""
                    },
                    {
                        "role": "user",
                        "content": f"Extract line items from this contractor quote:\n\n{text}"
                    }
                ]
            )

            result = response.choices[0].message.content.strip()
            json_start = result.find("[")
            json_end = result.rfind("]")
            if json_start != -1 and json_end != -1 and json_start < json_end:
                result = result[json_start:json_end+1]

            line_items = json.loads(result)
            if isinstance(line_items, list) and len(line_items) > 0:
                has_valid_items = any(item.get("material_name") for item in line_items if isinstance(item, dict))
                if has_valid_items:
                    use_vision = False
        except Exception as e:
            print(f"Text-based extraction failed, falling back to vision: {e}")

    if not use_vision:
        return line_items
    else:
        # Scanned PDF (no selectable text or text was watermarks/garbage) — fallback to Vision model
        all_items = []
        for page_num, page in enumerate(doc):
            # Render page to PNG at 2x resolution (144 DPI) for better OCR accuracy
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_bytes = pix.tobytes("png")
            base64_image = base64.b64encode(img_bytes).decode('utf-8')

            response = client.chat.completions.create(
                model="qwen/qwen3.6-27b",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a construction quote parser.
                        Extract all line items (including labor, services, and materials) from the quote image and return ONLY a JSON array.
                        Each item must have: material_name, quantity, unit, unit_price, total_price.
                        For total_price, extract the total cost of the line item (which includes both labor and material costs, typically under the 'Total Cost' or 'Amount' column). If the quote is broken down by Labour Cost and Materials Cost, use the combined 'Total Cost' for total_price.
                        If you cannot find a value, use null.
                        Return only the JSON array, no other text, no markdown, no backticks."""
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract all construction line items from this quote page image."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ]
            )

            # Extract JSON array by locating the outer square brackets [ and ]
            json_start = page_result.find("[")
            json_end = page_result.rfind("]")
            if json_start != -1 and json_end != -1 and json_start < json_end:
                page_result = page_result[json_start:json_end+1]

            try:
                page_items = json.loads(page_result)
                if isinstance(page_items, list):
                    all_items.extend(page_items)
            except Exception as e:
                print(f"Failed to parse JSON on page {page_num}: {e}")

        return all_items
import fitz
import json
from groq import Groq
from config import settings

client = Groq(api_key=settings.groq_api_key)

def parse_pdf(file_bytes: bytes) -> list:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """You are a construction quote parser. 
                Extract line items from the quote text and return ONLY a JSON array.
                Each item must have: material_name, quantity, unit, unit_price, total_price.
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
    if result.startswith("```"):
        result = result.split("```")[1]
        if result.startswith("json"):
            result = result[4:]

    line_items = json.loads(result)
    return line_items
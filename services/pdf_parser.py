import fitz
import os
import json
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def parse_pdf(file_bytes: bytes) -> list:
    # Step 1 — extract raw text
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()

    # Step 2 — send to Groq to structure it
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

    # Step 3 — parse JSON response
    result = response.choices[0].message.content.strip()
    
    # Remove markdown backticks if Groq adds them
    if result.startswith("```"):
        result = result.split("```")[1]
        if result.startswith("json"):
            result = result[4:]
    
    line_items = json.loads(result)
    return line_items
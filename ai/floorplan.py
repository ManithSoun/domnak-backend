import json
import os
import groq
import fitz
from dotenv import load_dotenv

load_dotenv()
client = groq.Client(api_key=os.getenv("GROQ_API_KEY"))

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def analyze_floorplan(pdf_path):
    raw_text = extract_text_from_pdf(pdf_path)
    if not raw_text.strip():
        return {"error": "No text found in PDF – maybe it's a scanned image. Use OCR or vision API."}

    prompt = f"""
You are an architect. Based on the following extracted text from a floor plan, extract:
- Total floor area (in square meters) if mentioned
- Number of rooms (bedrooms, bathrooms, living, kitchen, etc.)
- Any dimensions or measurements
- Estimate quantities of major materials (cement, bricks, tiles, paint) based on typical Cambodian construction.

Text:
{raw_text}

Return a JSON with keys: floor_area (number or null), rooms (object with counts), estimated_materials (array of {{material, unit, quantity}}).
Return ONLY the JSON.
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )
    result = response.choices[0].message.content.strip()
    if result.startswith("```json"):
        result = result[7:]
    if result.endswith("```"):
        result = result[:-3]
    return json.loads(result)

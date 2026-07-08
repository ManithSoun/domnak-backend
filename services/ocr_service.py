# services/ocr_service.py
import pytesseract
from PIL import Image
import io

def extract_text_from_floor_plan(image_bytes: bytes) -> str:
    """Extract text and measurements from floor plan image using OCR"""
    
    # Open image
    image = Image.open(io.BytesIO(image_bytes))
    
    # Preprocess for better OCR
    # Convert to grayscale, threshold, etc.
    
    # Extract text
    text = pytesseract.image_to_string(image)
    
    # Parse measurements (e.g., "5.2m x 4.8m", "Room: 12m²")
    import re
    dimensions = re.findall(r'(\d+\.?\d*)\s*[xX]\s*(\d+\.?\d*)\s*m', text)
    
    return {
        "raw_text": text,
        "dimensions": dimensions,
        "rooms_count": text.lower().count("room")
    }

# Then analyze extracted data with Groq
def generate_boq_from_ocr(extracted_data: dict) -> dict:
    """Use Groq to generate BOQ from OCR data"""
    prompt = f"""
    Based on this floor plan data, generate a Bill of Quantities:
    {extracted_data}
    
    Include: concrete volume, brick quantity, paint area, etc.
    """
    # Send to Groq for BOQ generation
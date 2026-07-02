from fastapi import APIRouter, UploadFile, File
from services.pdf_parser import parse_pdf
from core.logging import logger
from utils.response import success, error

router = APIRouter()

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        # validate file type
        if not file.filename.endswith('.pdf'):
            return error(message="Only PDF files are allowed", status_code=400)
        
        contents = await file.read()
        
        # validate file not empty
        if len(contents) == 0:
            return error(message="Uploaded file is empty", status_code=400)
        
        # validate file size — max 10MB
        if len(contents) > 10 * 1024 * 1024:
            return error(message="File too large — max 10MB allowed", status_code=400)
        
        line_items = parse_pdf(contents)
        
        # validate AI returned something
        if not line_items:
            return error(message="No line items found in PDF — make sure it contains a contractor quote", status_code=400)
        
        logger.info(f"PDF parsed: {file.filename} — {len(line_items)} items extracted")
        return success(data={"line_items": line_items})
    except Exception as e:
        logger.error(f"PDF parsing failed: {str(e)}")
        return error(message=str(e), status_code=400)
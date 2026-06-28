from fastapi import APIRouter, UploadFile, File, HTTPException
from services.pdf_parser import parse_pdf

router = APIRouter()

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        line_items = parse_pdf(contents)
        return {"line_items": line_items}  
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
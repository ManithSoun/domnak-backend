from typing import Any, Optional
from fastapi.responses import JSONResponse

def success(data: Any = None, message: Optional[str] = None, status_code: int = 200):
  return JSONResponse(
    status_code=status_code,
    content={
      "data": data,
      "message": message,
      "error": None
    }
  )
  
def error(message: str = "Something went wrong", code: str = "ERROR", status_code: int = 400):
  return JSONResponse(
    status_code=status_code,
    content={
      "data": None,
      "message": None,
      "error": {
        "message": message,
        "code": code
      }
    }
  )

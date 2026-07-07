from fastapi.responses import JSONResponse

def success(data=None, message=None, status_code=200):
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success",
            "data": data,
            "message": message,
            "error": None
        }
    )

def error(message, status_code=500, data=None):
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "data": data,
            "message": None,
            "error": {"message": message, "code": "ERROR"}
        }
    )

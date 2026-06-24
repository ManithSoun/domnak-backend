import os
from fastapi import FastAPI, Header, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from services.supabase import supabase
from routes.auth import router as auth_router
from routes.quotes import router as quote_router
from routes.line_items import router as line_items_router
from routes.estimator import router as estimator_router
from routes.pdf import router as pdf_router
from routes.suppliers import router as suppliers_router

security = HTTPBearer()

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app_kwargs = {
    "title": "Domnak API",
    "swagger_ui_parameters": {"persistAuthorization": True}
}

if ENVIRONMENT == "production":
    app_kwargs["docs_url"] = None
    app_kwargs["redoc_url"] = None
    app_kwargs["openapi_url"] = None

app = FastAPI(**app_kwargs)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth")
app.include_router(quote_router, prefix="/api/quotes")
app.include_router(line_items_router, prefix="/api/line-items")
app.include_router(estimator_router, prefix="/api/estimator")
app.include_router(pdf_router, prefix="/api/pdf")
app.include_router(suppliers_router, prefix="/api/suppliers")

@app.get("/")
def root():
    return {"status": "Domnak API running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/health/ready")
def health_ready():
    try:
        supabase.table("suppliers").select("id").limit(1).execute()
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        return Response(content=f'{{"status": "not ready", "database": "disconnected", "error": "{str(e)}"}}', status_code=503)

@app.get("/test-db")
def test_db():
    data = supabase.table("suppliers").select("*").execute()
    return {"connected": True, "rows": len(data.data)}

@app.get("/test-token")
def test_token(authorization: str = Header(None)):
    return {"received": authorization}
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from db.supabase import supabase
from api.router import router

app_kwargs = {
    "title": "Domnak API",
    "swagger_ui_parameters": {"persistAuthorization": True}
}

if settings.environment == "production":
    app_kwargs["docs_url"] = None
    app_kwargs["redoc_url"] = None
    app_kwargs["openapi_url"] = None

app = FastAPI(**app_kwargs)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

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
        return Response(
            content=f'{{"status": "not ready", "database": "disconnected", "error": "{str(e)}"}}',
            status_code=503
        )
from fastapi import FastAPI, Depends
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from routes.quotes import router as quote_router
from routes.line_items import router as line_items_router
from routes.estimator import router as estimator_router
from routes.auth import router as auth_router
from routes import chat
from core.auth import get_current_user
import os
from dotenv import load_dotenv

# Import floor_plan router
from api.v1.floor_plan import router as floor_plan_router

load_dotenv()

app = FastAPI(
    title="Domnak API",
    description="Construction Cost Estimator API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(quote_router, prefix="/api/quotes", tags=["Quotes"])
app.include_router(line_items_router, prefix="/api/line-items", tags=["Line Items"])
app.include_router(estimator_router, prefix="/api/estimator", tags=["Estimator"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])

# Add floor_plan router
app.include_router(floor_plan_router, prefix="/api/v1/floor-plan", tags=["Floor Plan"])

@app.get("/")
def root():
    return {"status": "Domnak API running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/health/ready")
def health_ready():
    return {"status": "ready"}

@app.get("/test-db")
def test_db():
    from db.supabase import supabase
    try:
        result = supabase.table("quotes").select("count").execute()
        return {"status": "connected", "count": result.count}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/test-token")
def test_token(authorization: str = Depends(HTTPBearer())):
    return {"received": authorization}

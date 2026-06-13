from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.supabase import supabase
from routes.auth import router as auth_router
from routes.quotes import router as quote_router
from routes.line_items import router as line_items_router

app = FastAPI(title="Domnak API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth")
app.include_router(quote_router, prefix="/api/quotes")
app.include_router(line_items_router, prefix="/api/line-items")

@app.get("/")
def root():
    return {"status": "Domnak API running"}

@app.get("/test-db")
def test_db():
    data = supabase.table("suppliers").select("*").execute()
    return {"connected": True, "rows": len(data.data)}
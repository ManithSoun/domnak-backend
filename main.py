from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.supabase import supabase

app = FastAPI(title="BuildSafe API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "Domnak API running"}

@app.get("/test-db")
def test_db():
    data = supabase.table("suppliers").select("*").execute()
    return {"connected": True, "rows": len(data.data)}
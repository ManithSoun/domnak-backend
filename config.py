import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")
        self.jwt_secret = os.getenv("JWT_SECRET", "supersecret")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        self.port = int(os.getenv("PORT", 8000))
        self.debug = os.getenv("DEBUG", "False").lower() == "true"

settings = Settings()

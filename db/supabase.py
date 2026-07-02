from supabase import create_client
from dotenv import load_dotenv
from config import settings

supabase = create_client(
    settings.supabase_url,
    settings.supabase_service_key
)
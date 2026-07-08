import os
from groq import Groq
from dotenv import load_dotenv

# Load .env from current directory
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("❌ GROQ_API_KEY not found in .env")
    exit(1)

client = Groq(api_key=api_key)

try:
    models = client.models.list()
    print("✅ Available Groq Models:")
    print("-" * 50)
    for model in models.data:
        print(f"  • {model.id}")
except Exception as e:
    print(f"❌ Error fetching models: {e}")

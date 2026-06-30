import os
from dotenv import load_dotenv
import groq

load_dotenv()
client = groq.Client(api_key=os.getenv("GROQ_API_KEY"))

resp = client.chat.completions.create(
    model="llama-3.3-70b-versatile",   # ✅ updated model
    messages=[{"role": "user", "content": "Say hello"}],
)
print(resp.choices[0].message.content)
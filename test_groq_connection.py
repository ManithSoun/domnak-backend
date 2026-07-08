"""
Quick standalone sanity check: is my Groq API key valid and is the model responding?
Run this BEFORE testing through Postman/FastAPI — it isolates AI problems from API problems.
"""
import os
from groq import Groq

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("❌ GROQ_API_KEY is not set in your environment.")
    print("   Set it with: export GROQ_API_KEY=your_key_here")
    exit(1)

client = Groq(api_key=api_key)

print("Sending a test prompt to Groq (model: llama-3.3-70b-versatile)...")

try:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Reply with exactly the word: PONG"}],
        temperature=0
    )
    reply = response.choices[0].message.content.strip()
    print(f"✅ Groq responded: {reply}")
    print("Your AI key and model are working correctly.")
except Exception as e:
    print(f"❌ Groq call failed: {e}")

import os
import groq
from dotenv import load_dotenv

load_dotenv()
client = groq.Client(api_key=os.getenv("GROQ_API_KEY"))

def stream_chat(messages, system_prompt=None):
    system = system_prompt or "You are a helpful construction cost assistant. Answer questions about building materials, quotes, and construction in Cambodia."
    # Combine system with first user message for models that don't support system role
    if messages and messages[0]["role"] == "user":
        first_msg = messages[0]["content"]
        full_messages = [{"role": "user", "content": system + "\n\n" + first_msg}] + messages[1:]
    else:
        full_messages = [{"role": "user", "content": system}] + messages

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=full_messages,
        stream=True,
        temperature=0.7,
        max_tokens=1024,
    )
    for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

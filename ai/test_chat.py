from chatbot import stream_chat

messages = [{"role": "user", "content": "How can I save money on tiles?"}]
print("Bot: ", end="")
for chunk in stream_chat(messages):
    print(chunk, end="")
print()

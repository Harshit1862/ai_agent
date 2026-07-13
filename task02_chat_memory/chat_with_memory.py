from google import genai
from google.genai import types
from dotenv import load_dotenv
from pathlib import Path
import time
import os

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

chat = client.chats.create(
    model="gemini-flash-latest",
    config=types.GenerateContentConfig(
        system_instruction="""You are a helpful, concise assistant for learning AI development.
Rules:
- Keep answers short and practical
- Prefer Python examples when relevant
- If unsure, say so clearly instead of guessing
"""
    )
)

print("Chat started. Type 'exit' to quit.\n")

total_input_tokens = 0
total_output_tokens = 0

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break

    response = chat.send_message(user_input)
    print("AI:", response.text, "\n")

    # Track token usage for this turn
    usage = response.usage_metadata
    total_input_tokens += usage.prompt_token_count
    total_output_tokens += usage.candidates_token_count

print("--- Session Token Usage ---")
print(f"Total input tokens:  {total_input_tokens}")
print(f"Total output tokens: {total_output_tokens}")
print(f"Total tokens:        {total_input_tokens + total_output_tokens}")
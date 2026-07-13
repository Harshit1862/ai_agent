from google import genai
from google.genai import types
from dotenv import load_dotenv
from pathlib import Path
import os
import json

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

customer_message = """
Hi, I ordered a laptop stand 1 hour ago and it still hasn't arrived. 
Can i get details where my order is. 
Order number is ORD-48213.
"""

# response_schema forces the model to return JSON matching this exact structure
response_schema = {
    "type": "object",
    "properties": {
        "sentiment": {"type": "string", "enum": ["positive", "neutral", "negative"]},
        "urgency": {"type": "string", "enum": ["low", "medium", "high"]},
        "order_number": {"type": "string"},
        "issue_summary": {"type": "string"},
        "suggested_department": {"type": "string", "enum": ["shipping", "billing", "returns", "technical_support"]}
    },
    "required": ["sentiment", "urgency", "order_number", "issue_summary", "suggested_department"]
}

response = client.models.generate_content(
    model="gemini-flash-latest",
    contents=f"Analyze this customer support message:\n\n{customer_message}",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=response_schema
    )
)

# response.text is a JSON string -- parse it into a real Python dict
data = json.loads(response.text)

print(json.dumps(data, indent=2))
print("\n--- Accessing individual fields ---")
print("Urgency:", data["urgency"])
print("Route to:", data["suggested_department"])

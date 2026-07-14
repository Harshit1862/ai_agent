from google import genai
from google.genai import types
from dotenv import load_dotenv
from pathlib import Path
import os

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def check_order_status(order_number: str) -> str:
    """Simulates checking an order status in a database."""
    fake_db = {
        "ORD-48213": "Shipped, expected delivery in 2 days",
        "ORD-99999": "Delayed due to warehouse issue",
    }
    return fake_db.get(order_number, "Order number not found")

check_order_tool = types.Tool(function_declarations=[
    types.FunctionDeclaration(
        name="check_order_status",
        description="Check the current shipping status of a customer order using the order number.",
        parameters={
            "type": "object",
            "properties": {
                "order_number": {"type": "string", "description": "The order ID, e.g. ORD-99999"}
            },
            "required": ["order_number"]
        }
    )
])

user_message = "Hi, can you check the status of my order ORD-99999?"

response = client.models.generate_content(
    model="gemini-flash-latest",
    contents=user_message,
    config=types.GenerateContentConfig(tools=[check_order_tool])
)

part = response.candidates[0].content.parts[0]

if part.function_call:
    fn_call = part.function_call
    print(f"Model wants to call: {fn_call.name}({dict(fn_call.args)})")

    if fn_call.name == "check_order_status":
        result = check_order_status(**fn_call.args)
        print(f"Function result: {result}")

        follow_up = client.models.generate_content(
            model="gemini-flash-latest",
            contents=[
                types.Content(role="user", parts=[types.Part(text=user_message)]),
                types.Content(role="model", parts=[part]),  
                types.Content(role="user", parts=[types.Part(
                    function_response=types.FunctionResponse(
                        name="check_order_status",
                        response={"result": result}
                    )
                )])
            ],
            config=types.GenerateContentConfig(tools=[check_order_tool])
        )
        print("\nFinal AI response:", follow_up.text)
else:
    print("Model answered directly:", part.text)

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
    fake_orders = {
        "ORD-48213": "Delayed due to warehouse issue",
        "ORD-11111": "Delivered",
    }
    return fake_orders.get(order_number, "Order not found")

def check_refund_eligibility(order_number: str) -> str:
    fake_refund_rules = {
        "ORD-48213": "Eligible for refund due to delay (>5 days late)",
        "ORD-11111": "Not eligible, order already delivered on time",
    }
    return fake_refund_rules.get(order_number, "No refund data available")

available_functions = {
    "check_order_status": check_order_status,
    "check_refund_eligibility": check_refund_eligibility,
}

tools = types.Tool(function_declarations=[
    types.FunctionDeclaration(
        name="check_order_status",
        description="Check the current shipping status of an order.",
        parameters={
            "type": "object",
            "properties": {"order_number": {"type": "string"}},
            "required": ["order_number"]
        }
    ),
    types.FunctionDeclaration(
        name="check_refund_eligibility",
        description="Check whether an order is eligible for a refund.",
        parameters={
            "type": "object",
            "properties": {"order_number": {"type": "string"}},
            "required": ["order_number"]
        }
    ),
])

def run_agent(user_message: str, max_turns: int = 5):
    history = [types.Content(role="user", parts=[types.Part(text=user_message)])]

    for turn in range(max_turns):
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=history,
            config=types.GenerateContentConfig(tools=[tools])
        )

        part = response.candidates[0].content.parts[0]

        if part.function_call:
            fn_call = part.function_call
            fn_name = fn_call.name
            fn_args = dict(fn_call.args)
            print(f"[Turn {turn+1}] Model calls: {fn_name}({fn_args})")

            if fn_name in available_functions:
                result = available_functions[fn_name](**fn_args)
            else:
                result = f"Error: unknown function {fn_name}"
            print(f"[Turn {turn+1}] Result: {result}")

            history.append(types.Content(role="model", parts=[part]))
            history.append(types.Content(role="user", parts=[types.Part(
                function_response=types.FunctionResponse(
                    name=fn_name,
                    response={"result": result}
                )
            )]))
        else:
            print(f"\nFinal answer (after {turn+1} turn(s)):")
            print(part.text)
            return

    print("Max turns reached without a final answer.")

run_agent("Check the status of order ORD-48213, and if it's delayed, also check if it's eligible for a refund.")

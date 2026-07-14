from google import genai
from google.genai import types
from dotenv import load_dotenv
from pathlib import Path
import os
import time

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def check_order_status(order_number: str) -> str:
    fake_orders = {
        "ORD-48213": "Delayed due to warehouse issue",
        "ORD-11111": "Delivered",
    }
    if order_number not in fake_orders:
        raise ValueError(f"Order {order_number} not found in system")
    return fake_orders[order_number]

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


def call_model_with_retry(history, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.models.generate_content(
                model="gemini-flash-latest",
                contents=history,
                config=types.GenerateContentConfig(tools=[tools])
            )
        except Exception as e:
            error_str = str(e)
            if "RESOURCE_EXHAUSTED" in error_str or "429" in error_str:
                print(f"[Rate limit hit] Quota exceeded — stopping retries (waiting won't help within seconds).")
                return None  # don't burn retries on a quota error
            elif attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"[API error: {e}] Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"[API error] Failed after {max_retries} attempts: {e}")
                return None
    return None

def execute_tool_safely(fn_name: str, fn_args: dict) -> str:
    """Executes a tool call, catching errors so the agent doesn't crash --
    instead it gets a clear error message it can reason about."""
    if fn_name not in available_functions:
        return f"Error: '{fn_name}' is not a recognized tool."

    try:
        return available_functions[fn_name](**fn_args)
    except TypeError as e:
        return f"Error: invalid arguments for {fn_name} -- {e}"
    except ValueError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Error: unexpected failure in {fn_name} -- {e}"


def run_agent(user_message: str, max_turns: int = 5):
    history = [types.Content(role="user", parts=[types.Part(text=user_message)])]

    for turn in range(max_turns):
        response = call_model_with_retry(history)

        if response is None:
            print("Agent stopped: could not reach the model after retries.")
            return

        part = response.candidates[0].content.parts[0]

        if part.function_call:
            fn_call = part.function_call
            fn_name = fn_call.name
            fn_args = dict(fn_call.args)
            print(f"[Turn {turn+1}] Model calls: {fn_name}({fn_args})")

            result = execute_tool_safely(fn_name, fn_args)
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


run_agent("Check the status of order ORD-99999 and tell me if it's eligible for a refund.")

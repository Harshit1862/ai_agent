## Progress Log
- **Task 1**: Environment setup (venv, .env, .gitignore). First successful Gemini API 
  call using google-genai SDK. Learned system/user roles, structured request/response flow.

- **Task 2**: Multi-turn chat with memory using `client.chats.create()`. Learned how 
  conversation history is resent on every call (statelessness). Added custom system 
  instructions and token usage tracking via `usage_metadata`.

- **Task 3**: Structured JSON output using `response_schema` + `response_mime_type`. 
  Learned constrained decoding — how the model is restricted to only valid schema-matching 
  tokens. Tested classification reliability across sentiment/urgency/department fields.

- **Task 4**: Single tool-calling agent — model decides to call a Python function 
  (`check_order_status`), code executes it, result is fed back for a final natural-language 
  answer. Hit and resolved a real API issue: Gemini's newer "thinking" models require 
  `thought_signature` to be preserved and replayed exactly when re-sending function-call 
  history — solved by reusing the original response part object instead of rebuilding it.

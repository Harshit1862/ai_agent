## Progress Log
- **Day 1**: Environment setup (venv, .env, .gitignore). First successful Gemini API 
  call using google-genai SDK. Learned system/user roles, structured request/response flow.

  - **Day 2**: Multi-turn chat with memory using `client.chats.create()`. Learned how 
  conversation history is resent on every call (statelessness). Added custom system 
  instructions and token usage tracking via `usage_metadata`. Encountered and diagnosed 
  a transient 503 server error (Gemini high-demand throttling).


 - **Day 3**: Structured JSON output using `response_schema` + `response_mime_type`. 
  Learned constrained decoding — how the model is restricted to only valid schema-matching 
  tokens. Tested classification reliability across sentiment/urgency/department fields 
  with varied customer message scenarios.
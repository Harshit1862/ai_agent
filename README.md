# AI Agent Fundamentals

A hands-on, from-first-principles progression through the core patterns behind
LLM agents — plain API calls, statelessness and memory, constrained/structured
output, single and multi-tool function calling, and production-grade error
handling — built directly against the **Gemini API** (`google-genai` SDK),
with no agent framework in between.

Each task is a small, self-contained script that builds on the concept before
it, so the reasoning loop underneath frameworks like LangChain is fully
visible and understood rather than assumed.

## What's covered

| Task | Concept | What it demonstrates |
|---|---|---|
| [`task01_api_basics`](task01_api_basics) | First API call | Minimal `google-genai` setup: client init, a single `generate_content` call, system/user roles |
| [`task02_chat_memory`](task02_chat_memory) | Statelessness & memory | Multi-turn chat via `client.chats.create()`; conversation history is resent on every call; token usage tracked via `usage_metadata` |
| [`task03_structured_json`](task03_structured_json) | Constrained decoding | Forcing valid JSON output with `response_schema` + `response_mime_type`; tested against a multi-field classification task (sentiment/urgency/department) |
| [`task04_tool_calling`](task04_tool_calling) | Single-tool function calling | Model decides to call a Python function, the function executes, and the result is fed back for a final natural-language answer |
| [`task05_agent_loop`](task05_agent_loop) | Multi-tool agent loop | A real ReAct-style loop: the model chooses between multiple tools across turns via dynamic dispatch (`available_functions` dict, no if/elif chain), bounded by a `max_turns` safety limit |
| [`task06_error_handling`](task06_error_handling) | Resilience | Exponential backoff on transient API failures, and safe tool execution that catches exceptions and feeds clean error messages back into the agent's reasoning loop instead of crashing |

## Notable things learned along the way

- **Statelessness is the whole game.** "Memory" in `task02` is just resending
  the full conversation history on every call — there's no server-side state.
- **Structured output is constrained decoding**, not prompt-engineered hope —
  `response_schema` restricts the model to only schema-valid tokens.
- **Thinking models replay function-call history literally.** Gemini's newer
  "thinking" models require `thought_signature` to be preserved and replayed
  *exactly* when re-sending function-call history; the fix in `task04` was to
  reuse the original response `Part` object rather than reconstructing it.
- **Dynamic dispatch beats branching.** `task05` routes tool calls through an
  `available_functions` dict instead of an `if/elif` chain, so adding a new
  tool doesn't touch the routing logic.
- **Failures should be observations, not crashes.** `task06` treats a failed
  tool call as data fed back into the loop (the agent sees "order not found"
  and can react), and wraps the API call itself in exponential backoff for
  transient errors.

## Setup

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install google-genai python-dotenv
```

Create a `.env` file in the repo root with your [Gemini API key](https://aistudio.google.com/apikey):

```
GEMINI_API_KEY=your_key_here
```

> Note: `requirements.txt` in this repo is a full environment dump from a
> ROS2 dev machine and includes many unrelated packages — the two lines above
> are the only dependencies these scripts actually need.

## Running

Each task is a standalone script:

```bash
python task01_api_basics/basic_call.py
python task02_chat_memory/chat_with_memory.py
python task03_structured_json/structured_json.py
python task04_tool_calling/tool_calling_agent.py
python task05_agent_loop/agent_loop.py
python task06_error_handling/robust_agent.py
```

## Tech stack

Python · Gemini API (`google-genai` SDK) · `python-dotenv`

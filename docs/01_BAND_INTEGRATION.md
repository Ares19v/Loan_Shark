# Band Integration — The Real API, the Root-Cause Bug, and the Fix

> Source of truth: **docs.band.ai** (Human API + LangGraph SDK tutorial), fetched 2026-06-17.
> This is the most important engineering doc in the repo. The live demo lives or dies here.

---

## 1. Mental model

Band is a chat platform where **humans and agents are participants in chat rooms**. Agents are persistent WebSocket clients; they wake when a message **@mentions** them, run their logic, and post a reply by calling a tool. There are two API surfaces:

- **Agent API** (`/api/v1/agent/...`) — used *by the agents* (the Band SDK handles this for us).
- **Human API** (`/api/v1/me/...`) — used *by a human/user client*. **Our Streamlit UI is a "human"**, so it uses this surface to post the kickoff message and to poll for agent replies.

> The current `app.py` tried to use a made-up `rooms/{id}/messages` endpoint with an *agent* key. That endpoint doesn't exist. **Use the Human API.**

---

## 2. Authentication

**Base URL:** `https://app.band.ai/api/v1`

**Human API auth** (pick one header):
- `X-API-Key: <HUMAN_API_KEY>`  ← we use this
- `Authorization: Bearer <JWT>`  ← fallback if a personal API key isn't available

Get the human API key / token from your account on app.band.ai. Store it in `.env` as `BAND_HUMAN_API_KEY` (gitignored).

---

## 3. The two endpoints the UI needs

### 3.1 Post the kickoff message  (UI → room)
```
POST https://app.band.ai/api/v1/me/chats/{chat_id}/messages
Headers:  X-API-Key: <HUMAN_API_KEY>
          Content-Type: application/json
Body:
{
  "message": {
    "content": "@IntakeAgent NEW_LOAN_APPLICATION:\nApplicant: Priya Sharma, Age: 32 ...",
    "mentions": [
      { "handle": "<intake-agent-handle>" }
    ]
  }
}
```
- **⚠️ A message MUST include ≥1 `@mention` or Band will not route it to any agent.** This is the #1 reason the pipeline never triggered. The kickoff must `@mention` the Intake agent (both in the `content` text and in the `mentions` array).
- Success → `201` with `{ "data": { "id": "...", "chat_room_id": "...", "recipients": [...] } }`.

### 3.2 Poll for messages  (room → UI)
```
GET https://app.band.ai/api/v1/me/chats/{chat_id}/messages?since=<ISO8601>&limit=100
Headers:  X-API-Key: <HUMAN_API_KEY>
```
Query params:
- `since` — ISO-8601 datetime; returns messages after that instant. **Poll with `since = last seen inserted_at`.** (Cannot be combined with `cursor`.)
- `limit` — default 20, max 100.
- `cursor` / `next_cursor` — for pagination if needed.

Response shape:
```json
{
  "data": [
    {
      "id": "uuid",
      "content": "@RiskAgent RISK_ASSESSMENT:\n```json\n{...}\n```",
      "message_type": "text",
      "sender_id": "uuid",
      "sender_type": "Agent",          // "User" | "Agent"
      "sender_name": "RiskAgent",
      "chat_room_id": "uuid",
      "inserted_at": "2026-06-17T10:30:00Z",
      "updated_at": "2026-06-17T10:30:00Z",
      "metadata": {}
    }
  ],
  "metadata": { "has_more": true, "next_cursor": "...", "limit": 100 }
}
```
The UI runs `detect_message_stage(content)` on each new **Agent** message (skip `sender_type == "User"` to ignore the UI's own kickoff) and advances the pipeline.

---

## 4. How agents send/receive (Band SDK)

From the LangGraph tutorial. An agent is built exactly as our code already does:
```python
adapter = LangGraphAdapter(llm=ChatOpenAI(...), checkpointer=InMemorySaver(), system_prompt=PROMPT)
agent = Agent.create(adapter=adapter, agent_id=agent_id, api_key=api_key,
                     ws_url=os.getenv("BAND_WS_URL"), rest_url=os.getenv("BAND_REST_URL"))
await agent.run()
```

**Critical behavior to verify and respect:**
- The agent is triggered **only when @mentioned** in the room. (So each agent's output must `@mention` the next agent — our prompts already do this.)
- **The SDK does NOT automatically post the LLM's final text.** Per the docs: *"The LLM decides when to send messages using the `band_send_message` tool; the adapter automatically includes platform tools."* So the model must **call `band_send_message`** with the output content.

**Action item (T4):** confirm whether our installed `band-sdk` version auto-relays the assistant text or strictly requires the tool call. If the latter, every agent prompt must change from *"respond with exactly this format"* to *"**call the `band_send_message` tool** with content set to `@NextAgent TAG:` followed by the JSON block."* Verify by inspecting the installed package (`.venv/.../band/adapters/`) and by one live test.

---

## 5. The fix, as code (`band_client.py`)

A thin, dependency-light client the UI imports. (Reference implementation — final code lives in `band_client.py`.)
```python
import os, requests
from datetime import datetime, timezone

BASE = os.getenv("BAND_REST_URL", "https://app.band.ai/").rstrip("/") + "/api/v1"

def _headers() -> dict[str, str]:
    return {"X-API-Key": os.getenv("BAND_HUMAN_API_KEY", ""), "Content-Type": "application/json"}

def post_message(chat_id: str, content: str, mention_handle: str, *, timeout: float = 10.0) -> dict:
    """Post a @mention message to the room as the human user. Retries with backoff."""
    url = f"{BASE}/me/chats/{chat_id}/messages"
    body = {"message": {"content": content, "mentions": [{"handle": mention_handle}]}}
    return _request("POST", url, json=body, timeout=timeout)

def poll_messages(chat_id: str, since: str | None = None, *, limit: int = 100, timeout: float = 10.0) -> list[dict]:
    """Return room messages after `since` (ISO-8601). Newest pipeline state is derived by the caller."""
    url = f"{BASE}/me/chats/{chat_id}/messages"
    params = {"limit": limit}
    if since:
        params["since"] = since
    data = _request("GET", url, params=params, timeout=timeout)
    return data.get("data", [])

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
# _request() wraps requests with 3x exponential-backoff retry + explicit error raising (no silent None).
```

UI usage (in `app.py`):
```python
# Kickoff
content = build_application_message(form_data)        # now starts with "@IntakeAgent NEW_LOAN_APPLICATION:"
post_message(chat_id, content, intake_handle)
st.session_state.poll_since = now_iso()

# Auto-advance (inside a 2s st.fragment / st_autorefresh block)
for m in poll_messages(chat_id, st.session_state.poll_since):
    if m["sender_type"] != "Agent":
        continue
    st.session_state.poll_since = m["inserted_at"]
    stage = detect_message_stage(m["content"])
    # ... append to feed, set loan_decision / loan_letter, flip Human Gate ...
```

---

## 6. Runtime prerequisites (the live run won't work without these)

- [ ] 9 agents created on app.band.ai; record each **handle** (for `@mention`) — especially `intake` for kickoff.
- [ ] One room with all 9 agents added as participants; record **`chat_id`**.
- [ ] A **human API key** (or JWT) → `.env` `BAND_HUMAN_API_KEY`.
- [ ] `.env` `BAND_CHAT_ID` = the room id; `BAND_REST_URL=https://app.band.ai/`; `BAND_WS_URL=wss://app.band.ai/api/v1/socket/websocket`.
- [ ] `agent_config.yaml` with each agent's `agent_id` + `api_key`.
- [ ] `GROQ_API_KEY` in `.env`.

---

## 7. WebSocket (optional upgrade, not required for the demo)

For truly instant updates instead of 2s polling, Band exposes Phoenix-channel WebSockets (`wss://app.band.ai/api/v1/socket/websocket`) with human channels like `chat_room` emitting `message_created`. **Polling is simpler and good enough for the demo — only attempt WS if everything else is done.** Reference: docs.band.ai → `websocket/human/chat-room/message-created`.

---

## 8. Full endpoint index (for reference)

- Human messages: `GET|POST /me/chats/{chat_id}/messages` (list / send) ← **we use these**
- Human chats/rooms: `GET /me/chats`, `POST /me/chats` (create), `GET /me/chats/{id}`
- Human participants: `GET|POST|DELETE /me/chats/{id}/participants`
- Agent API (SDK-managed): `/agent/...` messages, events, peers, contacts, memories
- OpenAPI spec: `https://docs.band.ai/openapi.json`

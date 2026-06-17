"""
agents/base.py — shared bootstrap for all 9 Loan Shark Band agents.

Why this exists (two demo-blocking bugs this fixes centrally):

1. The installed ``LangGraphAdapter`` takes ``custom_section=`` (developer
   instructions), NOT ``system_prompt=``. Passing ``system_prompt=`` raises a
   TypeError and the agent never boots. We pass the persona prompt as
   ``custom_section``; the SDK wraps it with BASE_INSTRUCTIONS.

2. Band agents deliver output ONLY by calling the ``band_send_message`` tool
   ("Plain text output is not delivered"). The mention array must contain a
   valid handle (``@<username>/<agent-name>``). Each agent's prompt therefore
   gets a standardized "HOW TO SEND" block with the resolved next-agent handle.

Handles are account-specific, so they are configured via environment:
    BAND_USER_HANDLE        e.g. "trencoders"  -> default handle @trencoders/<AgentName>
    BAND_HANDLE_<KEY>       per-agent override, e.g. BAND_HANDLE_DOCUMENT=@team/doc-bot
    BAND_OPERATOR_HANDLE    the human loan officer to notify at the final step
See docs/01_BAND_INTEGRATION.md and .env.example.
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys

from dotenv import load_dotenv
from band import Agent
from band.adapters import LangGraphAdapter
from band.config import load_agent_config
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
import openai
import re
import time
import requests

DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

# Global list of Groq API keys for rotation to bypass rate limits
GROQ_API_KEYS = [
    os.getenv("GROQ_API_KEY"),
    "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",
    "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",
    "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"
]
# Filter out empty or None values
GROQ_API_KEYS = [k for k in GROQ_API_KEYS if k]
_CURRENT_KEY_INDEX = 0

def get_next_key() -> str | None:
    global _CURRENT_KEY_INDEX
    if not GROQ_API_KEYS:
        return None
    _CURRENT_KEY_INDEX = (_CURRENT_KEY_INDEX + 1) % len(GROQ_API_KEYS)
    new_key = GROQ_API_KEYS[_CURRENT_KEY_INDEX]
    os.environ["GROQ_API_KEY"] = new_key
    return new_key

def extract_thought(text: str) -> str:
    text = text.strip()
    # Split by any @mention (like @CreditAgent or @trencoders/creditagent)
    parts = re.split(r'@[a-zA-Z0-9_\-/]+', text)
    if parts:
        text = parts[0].strip()
    # Also strip code blocks
    if "```" in text:
        text = text.split("```")[0].strip()
    return text

def send_thought_event(api_key: str | None, chat_id: str | None, text: str) -> None:
    if not api_key or not chat_id or not text:
        return
    rest_url = os.getenv("BAND_REST_URL", "https://app.band.ai/").rstrip("/")
    url = f"{rest_url}/api/v1/agent/chats/{chat_id}/events"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-API-Key": api_key,
    }
    payload = {
        "event": {
            "content": text,
            "message_type": "thought"
        }
    }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=5.0)
        if r.status_code >= 400:
            print(f"[WARN] Failed to send thought event ({r.status_code}): {r.text[:200]}")
    except Exception as e:
        print(f"[WARN] Error sending thought event: {e}")

async def send_thought_event_async(api_key: str | None, chat_id: str | None, text: str) -> None:
    await asyncio.to_thread(send_thought_event, api_key, chat_id, text)


def should_rotate_key(e: Exception) -> bool:
    if isinstance(e, openai.APIError):
        # Rotate on key/auth errors (401), rate limits (429), payload/TPM errors (413), or 5xx server errors
        status_code = getattr(e, "status_code", None)
        if status_code in (401, 413, 429, 500, 502, 503, 504):
            return True
    err_str = str(e).lower()
    markers = ("rate limit", "rate_limit", "tpm", "limit", "429", "413", "401", "invalid_api_key", "unauthorized", "token", "too large")
    return any(marker in err_str for marker in markers)


def get_wait_time(e: Exception, attempt: int) -> float:
    err_str = str(e)
    # Search for "try again in X.XXs" or "try again in X.XXms" or similar
    match = re.search(r"try again in (?:(\d+)m)?(\d+\.?\d*)(s|ms)?", err_str, re.IGNORECASE)
    if match:
        minutes = float(match.group(1)) if match.group(1) else 0.0
        seconds = float(match.group(2))
        unit = match.group(3)
        val = minutes * 60.0 + seconds
        if unit and unit.lower() == "ms":
            val = val / 1000.0
        # Add a 1.5 second safety buffer
        wait_time = val + 1.5
        print(f"[RateLimit] Parsed wait time of {val}s from error. Sleeping for {wait_time:.2f}s (with safety buffer)...")
        return wait_time
    
    # Check headers if it's an APIError
    if isinstance(e, openai.APIError) and hasattr(e, "headers") and e.headers:
        # Groq might send standard RateLimit headers like retry-after
        retry_after = e.headers.get("retry-after") or e.headers.get("x-ratelimit-reset")
        if retry_after:
            try:
                val = float(retry_after)
                wait_time = val + 1.5
                print(f"[RateLimit] Found retry-after header: {val}s. Sleeping for {wait_time:.2f}s...")
                return wait_time
            except ValueError:
                pass

    # Progressive fallback if nothing found
    fallback = 3.0 * (attempt + 1)
    print(f"[RateLimit] No wait time found in error. Using progressive fallback of {fallback:.2f}s...")
    return fallback


class RateLimitedChatOpenAI(ChatOpenAI):
    def __init__(self, *args, agent_api_key: str | None = None, chat_id: str | None = None, agent_label: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__["agent_api_key"] = agent_api_key
        self.__dict__["chat_id"] = chat_id
        self.__dict__["agent_label"] = agent_label

    def _rotate_api_key(self, attempt: int, retries: int) -> bool:
        new_key = get_next_key()
        if new_key:
            print(f"[RateLimit] Groq Rate Limit/Error hit. Rotating API key (attempt {attempt + 1}/{retries})...")
            try:
                self.openai_api_key = new_key
                if hasattr(self, "client") and hasattr(self.client, "_client"):
                    self.client._client.api_key = new_key
                if hasattr(self, "async_client") and hasattr(self.async_client, "_client"):
                    self.async_client._client.api_key = new_key
            except Exception as err:
                print(f"[WARN] Error updating client key: {err}")
            return True
        return False

    async def _astream(self, messages, stop=None, run_manager=None, **kwargs):
        retries = 10
        for attempt in range(retries):
            try:
                chunks = []
                async for chunk in super()._astream(messages, stop=stop, run_manager=run_manager, **kwargs):
                    chunks.append(chunk)
                for chunk in chunks:
                    yield chunk

                text = "".join(c.content for c in chunks if hasattr(c, "content"))
                thought = extract_thought(text)
                if thought:
                    await send_thought_event_async(
                        self.__dict__.get("agent_api_key"),
                        self.__dict__.get("chat_id"),
                        thought
                    )
                return
            except Exception as e:
                if should_rotate_key(e):
                    if attempt == retries - 1:
                        raise
                    self._rotate_api_key(attempt, retries)
                    wait_time = get_wait_time(e, attempt)
                    await asyncio.sleep(wait_time)
                else:
                    raise

    def _stream(self, messages, stop=None, run_manager=None, **kwargs):
        retries = 10
        for attempt in range(retries):
            try:
                chunks = []
                for chunk in super()._stream(messages, stop=stop, run_manager=run_manager, **kwargs):
                    chunks.append(chunk)
                for chunk in chunks:
                    yield chunk

                text = "".join(c.content for c in chunks if hasattr(c, "content"))
                thought = extract_thought(text)
                if thought:
                    send_thought_event(
                        self.__dict__.get("agent_api_key"),
                        self.__dict__.get("chat_id"),
                        thought
                    )
                return
            except Exception as e:
                if should_rotate_key(e):
                    if attempt == retries - 1:
                        raise
                    self._rotate_api_key(attempt, retries)
                    wait_time = get_wait_time(e, attempt)
                    time.sleep(wait_time)
                else:
                    raise

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        retries = 10
        for attempt in range(retries):
            try:
                res = await super()._agenerate(messages, stop=stop, run_manager=run_manager, **kwargs)
                if res and res.generations:
                    text = res.generations[0].message.content
                    thought = extract_thought(text)
                    if thought:
                        await send_thought_event_async(
                            self.__dict__.get("agent_api_key"),
                            self.__dict__.get("chat_id"),
                            thought
                        )
                return res
            except Exception as e:
                if should_rotate_key(e):
                    if attempt == retries - 1:
                        raise
                    self._rotate_api_key(attempt, retries)
                    wait_time = get_wait_time(e, attempt)
                    await asyncio.sleep(wait_time)
                else:
                    raise

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        retries = 10
        for attempt in range(retries):
            try:
                res = super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
                if res and res.generations:
                    text = res.generations[0].message.content
                    thought = extract_thought(text)
                    if thought:
                        send_thought_event(
                            self.__dict__.get("agent_api_key"),
                            self.__dict__.get("chat_id"),
                            thought
                        )
                return res
            except Exception as e:
                if should_rotate_key(e):
                    if attempt == retries - 1:
                        raise
                    self._rotate_api_key(attempt, retries)
                    wait_time = get_wait_time(e, attempt)
                    time.sleep(wait_time)
                else:
                    raise


def build_llm(
    temperature: float = 0.1,
    agent_api_key: str | None = None,
    chat_id: str | None = None,
    agent_label: str | None = None,
) -> ChatOpenAI:
    """Construct the Groq (OpenAI-compatible) chat model shared by every agent."""
    return RateLimitedChatOpenAI(
        model=os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL),
        openai_api_key=os.getenv("GROQ_API_KEY"),
        openai_api_base=GROQ_BASE_URL,
        temperature=temperature,
        max_retries=0,        # Disable internal retries so we fail fast and rotate keys instantly!
        request_timeout=60,
        agent_api_key=agent_api_key,
        chat_id=chat_id,
        agent_label=agent_label,
    )


def resolve_handle(config_key: str, display_name: str) -> str:
    """Resolve the Band @mention handle for a downstream agent.

    Priority: explicit ``BAND_HANDLE_<KEY>`` override -> ``@<user>/<DisplayName>``
    -> ``@<DisplayName>`` as a last resort. Handles are account-specific; set
    BAND_USER_HANDLE (and per-agent overrides if your handles differ).
    """
    override = os.getenv(f"BAND_HANDLE_{config_key.upper()}", "").strip()
    if override:
        return override
    user = os.getenv("BAND_USER_HANDLE", "").strip().lstrip("@")
    return f"@{user}/{display_name.lower()}" if user else f"@{display_name.lower()}"



def _send_instructions(handle: str | None, output_tag: str) -> str:
    """Standardized 'how to deliver output' block appended to each prompt."""
    if handle:
        target = f'mentions=["{handle}"]'
        who = f"the next agent ({handle})"
    else:
        operator = os.getenv("BAND_OPERATOR_HANDLE", "").strip()
        if not operator:
            user = os.getenv("BAND_USER_HANDLE", "").strip().lstrip("@")
            operator = f"@{user}" if user else ""
        target = f'mentions=["{operator}"]' if operator else 'mentions=["@operator"]'
        who = "the human loan officer for review"
    return f"""

## HOW TO DELIVER YOUR OUTPUT (REQUIRED)
You MUST send your result by calling the `band_send_message` tool. Plain text
replies are NOT delivered to the room.
- Set `content` to your full output exactly as specified above: the `{output_tag}`
  header line followed by the ```json ... ``` block.
- Set `{target}` so it routes to {who}. At least one mention is required.
Call the tool exactly once. Do not also reply in plain text.
"""


def run_agent(
    *,
    config_key: str,
    label: str,
    system_prompt: str,
    output_tag: str,
    next_config_key: str | None = None,
    next_display_name: str | None = None,
    temperature: float = 0.1,
) -> None:
    """Boot and run one Band agent. Blocks (``await agent.run()``) until stopped."""

    async def _main() -> None:
        # Windows consoles default to cp1252; keep emoji/box output from crashing logs.
        for _stream in (sys.stdout, sys.stderr):
            try:
                _stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

        load_dotenv()

        agent_id, api_key = load_agent_config(config_key)

        CONCISE_THINKING_PROMPT = """

## CONCISE THINKING DIRECTIVE
To optimize performance, avoid rate limits, and keep the user response quick:
- Keep your internal reasoning or analysis extremely brief (1-2 sentences maximum).
- Explain your key finding or decision basis concisely as your reasoning, then output the required next-stage tag and the JSON block.
- Be concise, direct, and fast.
"""
        handle = (
            resolve_handle(next_config_key, next_display_name)
            if next_config_key and next_display_name
            else None
        )
        custom_section = system_prompt + CONCISE_THINKING_PROMPT + _send_instructions(handle, output_tag)

        adapter = LangGraphAdapter(
            llm=build_llm(temperature, api_key, os.getenv("BAND_CHAT_ID"), label),
            checkpointer=InMemorySaver(),
            custom_section=custom_section,
        )

        agent = Agent.create(
            adapter=adapter,
            agent_id=agent_id,
            api_key=api_key,
            ws_url=os.getenv("BAND_WS_URL"),
            rest_url=os.getenv("BAND_REST_URL"),
        )

        logging.basicConfig(
            level=logging.INFO,
            format=f"%(asctime)s [{label}] %(message)s",
            datefmt="%H:%M:%S",
        )
        logging.getLogger(config_key).info("%s agent running — listening on Band room...", label)
        await agent.run()

    asyncio.run(_main())

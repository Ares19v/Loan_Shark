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

DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"


def build_llm(temperature: float = 0.1) -> ChatOpenAI:
    """Construct the Groq (OpenAI-compatible) chat model shared by every agent."""
    return ChatOpenAI(
        model=os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL),
        openai_api_key=os.getenv("GROQ_API_KEY"),
        openai_api_base=GROQ_BASE_URL,
        temperature=temperature,
        max_retries=3,        # resilience against transient Groq errors
        request_timeout=60,
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
    return f"@{user}/{display_name}" if user else f"@{display_name}"


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

        handle = (
            resolve_handle(next_config_key, next_display_name)
            if next_config_key and next_display_name
            else None
        )
        custom_section = system_prompt + _send_instructions(handle, output_tag)

        adapter = LangGraphAdapter(
            llm=build_llm(temperature),
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

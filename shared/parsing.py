"""
shared/parsing.py — robust extraction of agent payloads from Band messages.

The agents post messages like:

    LOAN_APPLICATION:
    ```json
    { ... }
    ```

LLM output is not always perfectly formatted, so the UI must parse defensively.
This module replaces the old ``except: return None`` (which silently stalled the
pipeline) with tolerant extraction + light repair + explicit, logged failures.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# Fenced ```json ... ``` or ``` ... ``` block.
_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)
# Trailing commas before } or ] — the most common LLM JSON defect.
_TRAILING_COMMA_RE = re.compile(r",(\s*[}\]])")

# Pipeline tags in order; used to classify and validate messages.
STAGE_TAGS: tuple[str, ...] = (
    "NEW_LOAN_APPLICATION:",
    "LOAN_APPLICATION:",
    "DOC_VERIFICATION:",
    "CREDIT_ANALYSIS:",
    "FRAUD_REPORT:",
    "RISK_ASSESSMENT:",
    "COMPLIANCE_CHECK:",
    "LOAN_DECISION_READY:",
    "PRICING_TERMS:",
    "FORMAL_LETTER_READY:",
    "INTAKE_ERROR:",
)


def _repair(raw: str) -> str:
    """Best-effort cleanup of common LLM JSON defects before parsing."""
    cleaned = raw.strip()
    # Strip a leading "json" word if a bare fence was mislabeled.
    if cleaned.lower().startswith("json\n"):
        cleaned = cleaned[5:]
    cleaned = _TRAILING_COMMA_RE.sub(r"\1", cleaned)
    return cleaned


def _first_json_object(text: str) -> str | None:
    """Extract the first balanced ``{...}`` substring (fallback when no fence)."""
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    in_str = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start : i + 1]
    return None


def extract_json_from_message(text: str) -> dict[str, Any] | None:
    """Return the JSON payload embedded in an agent message, or None.

    Tries, in order: fenced ```json block, any fenced block, the first balanced
    {...} object. Applies light repair (trailing commas). Logs on failure rather
    than swallowing silently.
    """
    if not text:
        return None

    candidates: list[str] = [m.group(1) for m in _FENCE_RE.finditer(text)]
    fallback = _first_json_object(text)
    if fallback and fallback not in candidates:
        candidates.append(fallback)

    for candidate in candidates:
        for attempt in (candidate, _repair(candidate)):
            try:
                parsed = json.loads(attempt)
            except (json.JSONDecodeError, TypeError):
                continue
            if isinstance(parsed, dict):
                return parsed

    logger.warning("Could not extract JSON from message: %s", text[:160].replace("\n", " "))
    return None


def detect_stage_tag(text: str) -> str | None:
    """Return the pipeline tag present in the message, if any.

    Checks specific tags before the substring ``LOAN_APPLICATION:`` so that
    ``NEW_LOAN_APPLICATION:`` is not misread as ``LOAN_APPLICATION:``.
    """
    if not text:
        return None
    if "NEW_LOAN_APPLICATION:" in text:
        return "NEW_LOAN_APPLICATION:"
    for tag in STAGE_TAGS:
        if tag == "NEW_LOAN_APPLICATION:":
            continue
        if tag in text:
            return tag
    return None

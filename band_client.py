"""
band_client.py — Band Human API client for the Loan Shark Streamlit UI.

The Streamlit UI acts as a *human* participant in the Band room. It uses the
Band Human API to (1) post the kickoff loan application that @mentions the
Intake agent, and (2) poll the room for the agents' replies so the pipeline
advances automatically — no manual copy-paste.

Verified against docs.band.ai (Human API) on 2026-06-17. See
docs/01_BAND_INTEGRATION.md for the full contract and root-cause notes.

Endpoints used:
    POST {BASE}/me/chats/{chat_id}/messages   -> send a message (must @mention)
    GET  {BASE}/me/chats/{chat_id}/messages   -> list/poll messages

Auth: header "X-API-Key: <BAND_HUMAN_API_KEY>" (or "Authorization: Bearer <jwt>").
"""

from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from typing import Any

import requests

__all__ = [
    "BandClientError",
    "post_message",
    "poll_messages",
    "now_iso",
    "is_configured",
    "missing_config",
]

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

_DEFAULT_REST = "https://app.band.ai/"
_MAX_RETRIES = 3
_BACKOFF_BASE = 0.6  # seconds; 0.6, 1.2, 2.4


class BandClientError(RuntimeError):
    """Raised when the Band API cannot be reached or returns an error.

    We never silently swallow failures — the UI surfaces this to the operator.
    """


def _base_url() -> str:
    """Return the '.../api/v1' base, derived from BAND_REST_URL."""
    root = os.getenv("BAND_REST_URL", _DEFAULT_REST).rstrip("/")
    return f"{root}/api/v1"


def _headers() -> dict[str, str]:
    """Auth headers. Prefer X-API-Key; fall back to a Bearer JWT if provided."""
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    api_key = os.getenv("BAND_HUMAN_API_KEY", "").strip()
    jwt = os.getenv("BAND_HUMAN_JWT", "").strip()
    if api_key:
        headers["X-API-Key"] = api_key
    elif jwt:
        headers["Authorization"] = f"Bearer {jwt}"
    return headers


def is_configured() -> bool:
    """True when we have both a credential and a chat id to talk to."""
    return not missing_config()


def missing_config() -> list[str]:
    """Return the list of required env vars that are not set (for UI hints)."""
    missing: list[str] = []
    if not (os.getenv("BAND_HUMAN_API_KEY", "").strip() or os.getenv("BAND_HUMAN_JWT", "").strip()):
        missing.append("BAND_HUMAN_API_KEY (or BAND_HUMAN_JWT)")
    if not os.getenv("BAND_CHAT_ID", "").strip():
        missing.append("BAND_CHAT_ID")
    return missing


def now_iso() -> str:
    """Current UTC time as an ISO-8601 string, for the `since` poll cursor."""
    return datetime.now(timezone.utc).isoformat()


# ─────────────────────────────────────────────
# CORE REQUEST (retry + explicit errors)
# ─────────────────────────────────────────────

def _request(
    method: str,
    url: str,
    *,
    json_body: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    timeout: float = 10.0,
) -> dict[str, Any]:
    """Perform an HTTP request with exponential-backoff retry.

    Retries on network errors and 5xx/429. Raises BandClientError on final
    failure or on a 4xx that is not retryable.
    """
    last_error: Exception | None = None
    for attempt in range(_MAX_RETRIES):
        try:
            response = requests.request(
                method,
                url,
                headers=_headers(),
                json=json_body,
                params=params,
                timeout=timeout,
            )
        except requests.RequestException as exc:  # network/timeout
            last_error = exc
        else:
            if response.status_code < 400:
                if not response.content:
                    return {}
                try:
                    return response.json()
                except ValueError as exc:
                    raise BandClientError(
                        f"Band returned non-JSON ({response.status_code}): {response.text[:200]}"
                    ) from exc
            # Retry on transient server / rate-limit codes; fail fast otherwise.
            if response.status_code not in (429, 500, 502, 503, 504):
                raise BandClientError(
                    f"Band API {method} {url} -> {response.status_code}: {response.text[:300]}"
                )
            last_error = BandClientError(
                f"Band API transient {response.status_code}: {response.text[:200]}"
            )

        if attempt < _MAX_RETRIES - 1:
            time.sleep(_BACKOFF_BASE * (2 ** attempt))

    raise BandClientError(f"Band API {method} {url} failed after {_MAX_RETRIES} attempts: {last_error}")


# ─────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────

def post_message(
    chat_id: str,
    content: str,
    *,
    mention_handle: str | None = None,
    mentions: list[dict[str, str]] | None = None,
    timeout: float = 10.0,
) -> dict[str, Any]:
    """Post a message to the room as the human user.

    A message MUST include at least one @mention or Band will not route it to
    any agent — pass `mention_handle` (e.g. the Intake agent handle) or an
    explicit `mentions` list. The handle should also appear in `content`.

    Returns the created message's `data` dict.
    """
    if not chat_id:
        raise BandClientError("post_message: chat_id is required")

    mention_list = mentions if mentions is not None else (
        [{"handle": mention_handle}] if mention_handle else []
    )
    if not mention_list:
        raise BandClientError(
            "post_message: at least one @mention is required for Band to route the message"
        )

    url = f"{_base_url()}/me/chats/{chat_id}/messages"
    body = {"message": {"content": content, "mentions": mention_list}}
    result = _request("POST", url, json_body=body, timeout=timeout)
    return result.get("data", result)


def poll_messages(
    chat_id: str,
    since: str | None = None,
    *,
    limit: int = 100,
    timeout: float = 10.0,
) -> list[dict[str, Any]]:
    """List room messages, optionally only those after `since` (ISO-8601).

    Poll repeatedly with `since` = the last seen message's `inserted_at` to get
    only new messages. Returns the `data` list (possibly empty).
    """
    if not chat_id:
        raise BandClientError("poll_messages: chat_id is required")

    url = f"{_base_url()}/me/chats/{chat_id}/messages"
    params: dict[str, Any] = {"limit": limit}
    if since:
        params["since"] = since
    result = _request("GET", url, params=params, timeout=timeout)
    data = result.get("data", [])
    return data if isinstance(data, list) else []

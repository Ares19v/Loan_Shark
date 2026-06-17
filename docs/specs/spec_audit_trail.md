# Spec T6 — Live Audit Trail Panel + Export  (P1)

> **Owner:** Teammate (Gemini Antigravity). **File:** mostly `app.py` (one new self-contained render function + small helpers). Reuse the existing `st.session_state.agent_messages` list — that IS the audit trail.
> Paste this whole file into Antigravity in Planning mode. Follow `AGENTS.md` + `GEMINI.md`.

## 1. Objective
Make Loan Shark's compliance story **visible and exportable**: a panel that renders the full, timestamped agent conversation as a regulator-style audit trail, surfaces the exact compliance rule that drove the decision, and lets the officer download the record as **JSON and PDF**.

## 2. Why (the winning angle)
Track 3 is judged on "complete audit trail for regulatory review." We already capture every agent message; today it's hidden in a small feed. This turns it into the centerpiece: *"the Band room history is our immutable audit log — here it is, exportable for an RBI examination."*

## 3. User Stories
- As a **loan officer**, I can see the complete ordered trail of all 9 agents' outputs with timestamps.
- As a **compliance reviewer**, I can see which specific RBI rule / decision basis triggered the outcome, called out clearly (not buried).
- As an **auditor**, I can download the full record as JSON and as a formatted PDF.

## 4. Acceptance Criteria
- [ ] A new **"📋 Compliance Audit Trail"** expandable section renders below the agent feed whenever `st.session_state.agent_messages` is non-empty.
- [ ] It lists every message in order: agent/stage label, timestamp, and the parsed key fields (not raw 500-char dump). For messages with JSON, show a compact field table; keep raw JSON in a nested expander.
- [ ] A **"Decision basis"** callout shows `decision.compliance_notes` + `decision.decision_basis` (if present) + any `violations[]` from the compliance step, prominently.
- [ ] **Download JSON** button → the full `agent_messages` (with parsed payloads) as `audit_<application_id>.json`.
- [ ] **Download PDF** button → a formatted document: header (Loan Shark Financial Services, application id, generated-at), the ordered trail, and the final decision + human action. Use `reportlab` (already an intended dep) via `st.download_button(data=pdf_bytes, ...)`.
- [ ] Works for all 3 outcomes (APPROVE / COUNTER_OFFER / DENY).
- [ ] If `reportlab` isn't installed, the JSON export still works and the PDF button shows a clear "install reportlab" message instead of crashing.

## 5. Implementation Notes / Data Flow
- The audit data already exists: `st.session_state.agent_messages` = `list[{ "stage", "time", "text" }]`. Parse each `text` with the existing `extract_json_from_message()` to get structured fields.
- Implement as **one self-contained function** so it won't collide with the Band-integration rewrite:
  ```python
  def render_audit_panel(messages: list[dict], decision: dict | None, application_id: str | None) -> None: ...
  def build_audit_json(messages, decision, application_id) -> str: ...
  def build_audit_pdf(messages, decision, application_id) -> bytes: ...   # reportlab; wrap import in try/except
  ```
  The integration owner will call `render_audit_panel(...)` from the right column. Put these in a clearly marked `# ── AUDIT TRAIL ──` section near the other helpers.
- Stage→agent labels already exist in `app.py` (the `stage_label` dict in the feed) — reuse that mapping; don't invent new tag names.
- Add `reportlab` to `pyproject.toml` dependencies and `requirements.txt`.

## 6. Constraints
- Type hints + f-strings (per `AGENTS.md`). No bare `except`.
- Do **not** alter `detect_message_stage`, the message tags, or how messages are ingested — read-only consumer of `agent_messages`.
- Keep the dark theme; match existing CSS classes.

## 7. Out of Scope
- `band_client.py`, the agents, `shared/parsing.py`, the polling loop (Claude Code owns these).
- Real database persistence — the in-session list is enough for the demo.

## 8. Verification
- `uv run streamlit run app.py`; load **Good Applicant**, run the pipeline (or use the demo-safe replay from `spec_demo_and_pitch.md` if Band isn't wired yet), open the audit panel.
- Confirm ordered trail + decision-basis callout render; download JSON (valid, complete) and PDF (opens, readable).
- Repeat for High Risk (DENY) — denial reasons + violations appear.
- `uv run python preflight.py` → 0 FAIL. Screenshot all of the above into the Walkthrough.

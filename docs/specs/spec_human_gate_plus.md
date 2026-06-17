# Spec T7 — Human Gate++ (real human-in-the-loop)  (P1)

> **Owner:** Teammate (Gemini Antigravity). **File:** `app.py` (the Human Gate block, lines ~686–783) refactored into one self-contained function.
> Paste this whole file into Antigravity in Planning mode. Follow `AGENTS.md` + `GEMINI.md`.

## 1. Objective
Upgrade the Human Gate from a two-button stub into a **defensible human-in-the-loop control** — the feature that most directly wins Track 3's "human oversight at critical decision points."

## 2. User Stories
- As a **loan officer**, I enter my name before I can finalize, so the action is attributable.
- As an **officer**, when I **override** the AI, I must type a reason; the system records it.
- As an **officer**, on a COUNTER_OFFER I can adjust the approved amount/tenure before approving.
- As an **officer**, I must tick a short compliance checklist (KYC complete, terms reviewed) before "Approve & Finalize" is enabled.
- As an **auditor**, every human action is logged with officer name + timestamp + action type into the audit trail.

## 3. Acceptance Criteria
- [ ] An **"Officer name"** text input appears in the gate; **Approve** and **Override** are disabled until it's filled.
- [ ] A **compliance checklist** (≥3 checkboxes: "KYC verified", "Terms & EMI reviewed", "Decision basis acceptable") must all be checked to enable **Approve & Finalize**.
- [ ] **Override** opens a required **reason** text area; submitting with an empty reason is blocked with a clear message.
- [ ] For **COUNTER_OFFER**, the officer can edit `approved_amount` and `approved_tenure_months` in number inputs (pre-filled from the decision); the finalized values are what get logged.
- [ ] On Approve: append a `system` audit message like `✅ APPROVED by <officer> at <HH:MM:SS> — amount ₹X, tenure Y mo`. Set `pipeline_status = "complete"`.
- [ ] On Override: append `🚫 OVERRIDDEN by <officer> at <HH:MM:SS> — reason: "<reason>"`. 
- [ ] Existing decision summary card, financial metrics, formal-letter preview, and compliance expander are preserved.

## 4. Implementation Notes
- Refactor the current gate into:
  ```python
  def render_human_gate() -> None:
      """Reads st.session_state.loan_letter / loan_decision; renders gate; logs officer action."""
  ```
  Keep all existing rendering (badge map, metrics, letter preview) inside it. The integration owner calls `render_human_gate()` where the gate is today.
- Officer name / reason / checklist / edited amounts → store in `st.session_state` (e.g. `officer_name`, `override_reason`) so reruns don't lose them.
- Use Streamlit `st.button(..., disabled=<bool>)` for the enable/disable logic.
- Append actions to `st.session_state.agent_messages` (stage `"system"`) so they flow into the audit trail/export automatically.

## 5. Constraints
- Type hints + f-strings; no bare `except`.
- Do **not** remove the gate or let anything auto-finalize — the human step stays mandatory.
- Don't change message tags or the polling/agent code.
- Match existing CSS (`.human-gate`, `.decision-card`, badges).

## 6. Out of Scope
- Real auth / cryptographic signatures (a name + timestamp is enough for the demo).
- `band_client.py`, agents, parsing, audit export (T6 owns export — but your logged messages must be export-friendly).

## 7. Verification
- `uv run streamlit run app.py`; drive a COUNTER_OFFER (Borderline) to the gate.
- Confirm: buttons disabled until officer name + checklist; edit the amount; Approve logs officer + timestamp + final amount.
- Drive an APPROVE (Good) and a DENY (High Risk); on DENY, use Override with a reason → confirm it's logged and blocked when empty.
- `uv run python preflight.py` → 0 FAIL. Screenshot each path into the Walkthrough.

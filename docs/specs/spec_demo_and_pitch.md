# Spec T8 — Bulletproof Demo, Demo-Safe Mode, README & Video  (P1)

> **Owner:** Teammate (Gemini Antigravity). **Files:** `app.py` (a small, isolated "demo-safe replay" toggle), `README.md`, plus the submission video/text (outside the repo).
> Paste this whole file into Antigravity in Planning mode. Follow `AGENTS.md` + `GEMINI.md`.

## 1. Objective
Guarantee the demo cannot fail and that the project *reads* like a winner: (a) the 3 scenarios reliably produce APPROVE / COUNTER_OFFER / DENY, (b) a **demo-safe replay mode** that runs the full pipeline visually even if the live Band room hiccups, (c) a crisp README, (d) a 3-minute demo video.

## 2. Why
Live multi-agent demos break (network, quota, a slow agent). A judge sees the *story*, not the plumbing. We keep the real Band integration as the default, but carry a replay safety net so the on-stage run is flawless. The README + video are graded artifacts.

## 3. User Stories
- As a **presenter**, if the live room stalls, I flip "Demo-safe mode" and the same UI plays a realistic, pre-recorded pipeline end-to-end.
- As a **judge**, the README tells me the problem, the architecture, and how to run it in 60 seconds.
- As a **judge**, the 3-min video shows all 3 outcomes + the human gate + the audit trail.

## 4. Acceptance Criteria
- [ ] A small **"Demo-safe mode"** toggle (sidebar/checkbox). When ON, submitting a demo scenario **does not call Band**; instead it feeds a canned sequence of agent messages through the *existing* `detect_message_stage` path on a ~1.2s timer, so the 9 cards light up and the Human Gate appears exactly like the real run.
- [ ] Canned sequences exist for all 3 scenarios and yield APPROVE / COUNTER_OFFER / DENY respectively, with realistic JSON payloads (including `compliance_notes`, `letter_body`).
- [ ] When the toggle is OFF, behavior is the real Band post+poll (owned by the core integration workstream) — demo-safe mode must not break or bypass it.
- [ ] Canned data lives in a single `demo_replay.py` (or a clearly marked block) so it's easy to find and doesn't entangle real logic.
- [ ] **README.md** refreshed: 1-paragraph pitch, architecture diagram (the 9-agent flow), the winning thesis, accurate setup steps (uv, .env, agent_config.yaml, run_all, streamlit), and **reconciled vocabulary** (see `00_MASTER_PLAN.md` §10 — grades A+/A/B+/B/C/D/U, risk LOW/MEDIUM/HIGH/VERY_HIGH). No "LoanPilot" anywhere.
- [ ] A **`docs/DEMO_SCRIPT.md`** with the 3-min run-of-show (copy/expand from `00_MASTER_PLAN.md` §9) and a shot list for the video.

## 5. Implementation Notes
- Reuse the real ingestion path: in demo-safe mode, append each canned message to `st.session_state.agent_messages` and run the same stage detection + `loan_decision`/`loan_letter` capture the live poll loop uses, so downstream panels (audit, human gate) work identically.
- Build the canned payloads to match the actual agent JSON field names (see `agents/*/agent.py` system prompts and `00_MASTER_PLAN.md`). Pull realistic numbers from the existing `DEMO_SCENARIOS` dict.
- Use `st_autorefresh` or `st.fragment` for the replay timer; reuse whatever the integration owner adds for polling if it's already there — coordinate, don't duplicate.

## 6. Constraints
- Demo-safe mode is **additive and clearly labeled** — never silently fake a "real" run. It's a presenter safety net, disclosed as such.
- Don't change message tags, agents, or `band_client.py`.
- Type hints + f-strings; no bare `except`.

## 7. Out of Scope
- The real Band post/poll loop (core integration workstream).
- New agent logic.

## 8. Verification
- Toggle Demo-safe ON; run all 3 scenarios → correct outcomes, all 9 cards animate, Human Gate + audit panel populate. Screenshot each.
- Toggle OFF → confirm the real path is untouched (with creds, it posts to Band).
- README renders correctly on GitHub; setup steps are accurate; no "LoanPilot".
- `uv run python preflight.py` → 0 FAIL. Record the 3-min video per `docs/DEMO_SCRIPT.md`.

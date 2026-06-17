# Loan Shark — Master Plan & Objectives
### Band of Agents Hackathon 2026 · Track 3: Regulated & High-Stakes Workflows · Team TrenCoders

> **This is the north-star document. Everyone reads this first.**
> Submission: **June 19**. Must be demo-ready by **end of June 18**.
> Companion docs: [`01_BAND_INTEGRATION.md`](01_BAND_INTEGRATION.md) · [`02_TEAMMATE_GUIDE_ANTIGRAVITY.md`](02_TEAMMATE_GUIDE_ANTIGRAVITY.md) · specs in [`specs/`](specs/)

---

## 0. TL;DR — what we are doing and why

We already have a 9-agent loan pipeline. It *looks* finished but the **live demo does not actually run end-to-end** — the Streamlit UI can't really talk to Band, so today it needs manual copy-paste 9 times. **No judge will be impressed by copy-paste.**

This plan does three things in ~1 day:
1. **Fix the make-or-break:** make the demo run **fully automatically** — one form submit → all 9 agents → Human Gate, zero pasting. *(Owner: Navnit + Claude Code)*
2. **Add the regulated-workflow "wow":** live audit trail, exportable decision record, a stronger Human Gate. *(Owners: teammates in Antigravity)*
3. **Nail the pitch:** bulletproof 3 demo scenarios + a tight demo video + clean README. *(Owner: teammate)*

---

## 1. The winning thesis (say this to the judges)

> **"Loan Shark turns a 3–14 day, fragmented, inconsistent loan process into a minutes-long pipeline of 9 specialized AI agents — where Band's message room IS the immutable compliance audit trail, RBI rules are a hard regulatory gate no AI can override, and every final decision still requires a human loan officer's signature. AI advises. Humans decide. Band records everything."**

Three pillars, each a direct Track-3 hit:
- **Audit trail for free** — coordination layer == compliance log.
- **Compliance as a hard gate** — the Compliance Agent can block any approval; the AI cannot override it.
- **Human authority** — mandatory Human Gate; the officer can override any recommendation.

---

## 2. Objectives (what "win" means, concretely)

| # | Objective | Measure of done |
|---|---|---|
| O1 | The demo runs end-to-end with **no manual pasting** | Click a demo → 9 cards auto-light → Human Gate appears, all from one submit |
| O2 | All **3 outcomes** reproducible on demand | Good→APPROVE, Borderline→COUNTER_OFFER, High Risk→DENY, every time |
| O3 | **Regulated-workflow story is visible** | UI shows the live Band audit trail + the exact compliance rule + an exportable record |
| O4 | **Human-in-the-loop is undeniable** | Officer must approve/override; override needs a reason; action is timestamped + logged |
| O5 | **Robust under demo pressure** | A slow/failed agent or malformed JSON degrades gracefully, never a silent hang |
| O6 | **Deep Band integration is evident** | Remove Band and the whole thing collapses — UI posts + polls via the real Band Human API |
| O7 | **Submission assets ready** | 3-min video, README, repo on `main`, deployed URL (stretch) |

---

## 3. Architecture

### 3.1 The pipeline (unchanged — it's good)
9 agents, strict sequential, `@mention` hand-offs over a single Band room. Each agent enriches a cumulative JSON payload. See [`AGENTS.md` §3](../AGENTS.md) for the full tag protocol.

```
Applicant ─→ Streamlit UI ─(Band Human API: POST @IntakeAgent)─→ Band Room
  Intake → Document → Credit → Fraud → Risk → Compliance → Decision → Pricing → Communication
                                                                                      │
Streamlit UI ←─(Band Human API: GET messages, poll every 2s)─── Band Room ←──────────┘
        │
        └─→ HUMAN GATE (loan officer approves / overrides) → audit trail finalized
```

### 3.2 What changes — the real-time loop (the fix)
**Today (broken):** UI posts to a guessed REST URL with an agent key and no `@mention`; agent messages must be pasted in by hand.

**New (working):** UI uses the **Band Human API**:
- **Kick off:** `POST /api/v1/me/chats/{chat_id}/messages` with `X-API-Key`, body `@IntakeAgent NEW_LOAN_APPLICATION: …` (with a `mentions` entry).
- **Auto-advance:** poll `GET /api/v1/me/chats/{chat_id}/messages?since=<ts>` every ~2s; each new agent message advances the tracker, feed, and Human Gate automatically.

Full details and exact contracts: [`01_BAND_INTEGRATION.md`](01_BAND_INTEGRATION.md).

---

## 4. Judging-criteria alignment (Track 3)

| Track 3 criterion | How Loan Shark wins it | Where in code | Owner |
|---|---|---|---|
| Human oversight at critical points | Mandatory Human Gate; override with logged reason, officer name, timestamp | `app.py` Human Gate | Teammate — [`spec_human_gate_plus`](specs/spec_human_gate_plus.md) |
| Complete audit trail for regulatory review | Band room history shown live + exportable JSON/PDF; each decision cites its rule | `app.py` audit panel | Teammate — [`spec_audit_trail`](specs/spec_audit_trail.md) |
| Compliance with domain regulations | Compliance Agent = hard RBI gate; UI surfaces the triggered rule | `agents/compliance` + UI | Navnit + teammate |
| Structured, reproducible decisions | Deterministic guard re-checks hard blocks in code, not just LLM text | `agents/decision` + validator | Navnit |
| Multi-agent coordination | 9 agents over Band `@mention`, auto-advancing live | all agents + `band_client.py` | **Navnit (core)** |
| Error handling / graceful degradation | Retry + robust JSON parse + `INTAKE_ERROR` halt + stalled-agent UI state | `shared/parsing.py`, `app.py` | **Navnit (core)** |
| Deep Band SDK integration | Real Human API post+poll; agents reply via `band_send_message` | `band_client.py`, agents | **Navnit (core)** |

---

## 5. Honest current state (audit summary)

✅ **Works:** all 9 agents fully implemented with real domain logic; consistent Band/LangGraph/Groq setup; polished Streamlit UI; 94-check preflight; correct tag protocol.

⚠️ **Broken / risky (must fix):**
1. **UI↔Band loop is fake** — wrong REST URL + agent key + kickoff has **no `@mention`** → pipeline never triggers; falls back to manual paste. *(P0)*
2. **Agents may not actually post** — prompts say "respond with this text," but Band sends via the `band_send_message` tool. Needs verification + prompt fix. *(P0)*
3. **Fragile parsing** — bare `except: return None`; one malformed JSON silently stalls the pipeline. *(P0)*
4. **No retry / health** — a slow Groq call or dropped agent hangs with no signal. *(P0/P1)*
5. **Dead code** — `schema/messages.py` is unused 3-agent-era code. *(P1 cleanup)*
6. **Thin audit/human-gate** — no live Band history, no export, no override reason/timestamp. *(P1)*
7. **Doc drift** — PDF/README claim grades A+…F & `CRITICAL` risk, but code uses A+/A/B+/B/C/D/U & `VERY_HIGH`. *(P1 — see §10)*

---

## 6. The Task Board

Priorities: **P0 = the demo is dead without it. P1 = this is how we actually win. P2 = bonus if time remains.**
Owners: **CC = Navnit + Claude Code. TM = teammate (Gemini Antigravity).**
Each teammate task has a full spec in [`specs/`](specs/). Update the Status box as you go.

### P0 — Make it work (CC, critical path)
- [ ] **T1. Band Human API client** (`band_client.py`): `post_message` + `poll_messages`, `X-API-Key`, retry/timeout. → [`01_BAND_INTEGRATION.md`](01_BAND_INTEGRATION.md)
- [ ] **T2. Rewire `app.py`**: kickoff `@mention`s Intake; 2s auto-poll auto-advances the pipeline; creds become `BAND_HUMAN_API_KEY` + `BAND_CHAT_ID`; manual paste demoted to hidden fallback.
- [ ] **T3. Robust parsing** (`shared/parsing.py`): fence-tolerant JSON extract + Pydantic stage validation + Groq retry wrapper.
- [ ] **T4. Agent send-path fix**: verify `band_send_message` behavior; update all 9 prompts to *call the tool*; confirm model id consistent.
- [ ] **T5. Live run on a real Band room**: 9 agents up, room created, end-to-end green for all 3 scenarios.

### P1 — Win the track (TM, parallel)
- [ ] **T6. Audit trail panel + export** — [`spec_audit_trail.md`](specs/spec_audit_trail.md)
- [ ] **T7. Human Gate++** (override reason, modify amount, officer + timestamp, compliance checklist) — [`spec_human_gate_plus.md`](specs/spec_human_gate_plus.md)
- [ ] **T8. Demo + pitch + README + 3-min video** — [`spec_demo_and_pitch.md`](specs/spec_demo_and_pitch.md)
- [ ] **T9. Deterministic decision guard** (CC) — code re-checks hard blocks so verdicts are reproducible.
- [ ] **T10. Doc/code reconciliation** (CC + TM) — align README/PDF to actual grade/risk vocab (§10).

### P2 — Bonus (TM, only if ahead)
- [ ] **T11. Document upload → Document Agent** — [`spec_document_upload.md`](specs/spec_document_upload.md)
- [ ] **T12. Streamlit Cloud deploy** — [`spec_deploy.md`](specs/spec_deploy.md)

---

## 7. Timeline (≈1 day, parallelized)

| Block | CC (Navnit + Claude Code) | TM (teammates in Antigravity) |
|---|---|---|
| **1. Kickoff** | Docs + specs pushed to `main` ✅ (this set) | Pull repo, read this + your spec, set up Antigravity |
| **2. Core build** | T1–T4 (Band client, app rewire, parsing, agents) | T6 audit panel, T7 Human Gate++ (against current `app.py`) |
| **3. Integrate** | T5 live Band run; merge teammate UI work | T8 demo scenarios + README; help test |
| **4. Lock** | T9 guard, T10 reconcile, final preflight | Record 3-min video, finalize submission text |
| **5. Buffer** | Bug-fix from dry-run | P2 (doc upload / deploy) if time |

> **Coordination note:** T2 (CC) and T6/T7 (TM) all edit `app.py`. To avoid conflicts: TM builds audit/human-gate as **self-contained functions** (e.g. `render_audit_panel()`, `render_human_gate()`) that CC wires into the rewired `app.py`. Specs say this explicitly. Pull before you push; commit small.

---

## 8. Credentials & prerequisites (get these BEFORE the live run)

On [app.band.ai](https://app.band.ai) (use promo **BANDHACK26** for free Pro):
- [ ] Create **9 agents**: IntakeAgent, DocumentAgent, CreditAgent, FraudAgent, RiskAgent, ComplianceAgent, DecisionAgent, PricingAgent, CommunicationAgent. Note each one's **UUID**, **API key**, and **@mention handle**.
- [ ] Create **1 room** ("LoanShark") and add all 9 agents as participants. Note the **chat/room id** (`chat_id`).
- [ ] Get a **Human/User API key** (or JWT) for the UI to post + poll. → see [`01_BAND_INTEGRATION.md`](01_BAND_INTEGRATION.md).
- [ ] [console.groq.com](https://console.groq.com) → a **GROQ_API_KEY** (free tier).

Then locally (these files are **gitignored — never commit them**):
- [ ] `.env` ← from `.env.example`: `GROQ_API_KEY`, `BAND_HUMAN_API_KEY`, `BAND_CHAT_ID`, Band URLs.
- [ ] `agent_config.yaml` ← 9 agents' `agent_id` + `api_key`.
- [ ] `uv sync` → `uv run python preflight.py` → `uv run python run_all.py` → `uv run streamlit run app.py`.

---

## 9. The 3-minute demo script (rehearse this)

1. **(20s) Hook.** "Loan approvals take 3–14 days and two identical applicants can get different answers. We built Loan Shark: 9 AI agents that decide in minutes — but a human always signs, and every step is auditable."
2. **(15s) Show the room.** Show the Band room with all 9 agents — "this is our coordination layer *and* our audit trail, same thing."
3. **(45s) Good Applicant → APPROVE.** Click demo → submit → watch the 9 cards light up live (no pasting) → Human Gate shows the sanction letter → point at the live audit trail + the cited RBI rule → click **Approve**.
4. **(30s) High Risk → DENY.** Click demo → submit → Compliance Agent hard-blocks → DENY with reasons → "the AI *cannot* override compliance."
5. **(30s) Human authority.** On a borderline COUNTER_OFFER, click **Override**, type a reason → show it logged with officer + timestamp. "AI advises; the human decides."
6. **(20s) Close.** Export the audit record. "Minutes not weeks, consistent, fully audited, human-controlled — and it only works because Band routes and records every agent. That's Track 3."

---

## 10. Doc ↔ code reconciliation (don't let a judge catch a mismatch)

**Code is the source of truth.** The PDF/README must be corrected to match:
- Credit grades: code = **A+ / A / B+ / B / C / D / U** (U = unscored). PDF wrongly says `…F`. Decision logic must not reference a grade "F" that never exists.
- Risk category: code = **LOW / MEDIUM / HIGH / VERY_HIGH**. PDF says `CRITICAL`.
- Doc verdict: code = **CLEAR / FLAGGED / CRITICAL**. PDF says `COMPLETE/PARTIAL/INSUFFICIENT`.
- Compliance verdict: code = **COMPLIANT / COMPLIANT_WITH_CONDITIONS / NON_COMPLIANT / EDD_REQUIRED**.
- `generate_pdf.py` + `reportlab` are referenced in the PDF but not in the repo — drop the reference or re-add the file.

---

## 11. Definition of Done (submission checklist)

- [ ] O1–O6 all demonstrably true on a fresh machine following §8.
- [ ] `preflight.py`: 0 FAIL (warnings only for unfilled creds).
- [ ] 3 scenarios pass live, no pasting.
- [ ] Audit record exports and reconstructs the full chain.
- [ ] Human override logs reason + officer + timestamp.
- [ ] README reconciled to code; no "LoanPilot" anywhere.
- [ ] No secrets committed; `.env` + `agent_config.yaml` gitignored.
- [ ] 3-min demo video recorded; submission text written.
- [ ] Everything on `main`, pushed.

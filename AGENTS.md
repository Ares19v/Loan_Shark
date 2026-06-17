# AGENTS.md — Loan Shark Project Rules

> This file is read automatically by AI coding agents (Gemini Antigravity, Cursor, etc.).
> It defines the non-negotiable rules for working in this repo. **Read it before writing any code.**
> Antigravity users: `GEMINI.md` adds Antigravity-specific behavior on top of this file.

---

## 1. Project Overview

**Loan Shark** is a 9-agent AI loan-processing pipeline for the **Band of Agents Hackathon 2026, Track 3 (Regulated & High-Stakes Workflows)**. Team **TrenCoders**.

A loan applicant submits a form in a Streamlit UI → the message is posted to a **Band** chat room → 9 specialized AI agents process it sequentially via `@mention` hand-offs → a human loan officer signs off at a mandatory **Human Gate**. Three outcomes: **APPROVE / DENY / COUNTER_OFFER**.

**The single most important idea:** Band's room message history *is* the immutable compliance audit trail, and **AI is advisory only — a human makes the final call.**

Before changing anything, read **`docs/00_MASTER_PLAN.md`** (the objectives + task board) and **`docs/01_BAND_INTEGRATION.md`** (how the platform actually works).

---

## 2. Tech Stack (do not swap without team sign-off)

| Layer | Tech | Notes |
|---|---|---|
| Agent coordination | **Band SDK** (`band-sdk[langgraph]`) | The ONLY inter-agent transport. `@mention` is the sole hand-off mechanism. |
| Agent runtime | **LangGraph** | Each agent = `LangGraphAdapter` + `InMemorySaver`. |
| LLM | **Groq** `llama-3.3-70b-versatile` | Via `langchain-openai` `ChatOpenAI`, base_url `https://api.groq.com/openai/v1`. |
| Frontend | **Streamlit** (`app.py`) | Form + live pipeline tracker + Human Gate. |
| Language | **Python 3.11+** | |
| Package manager | **uv** (Astral) | `uv sync`, `uv run python ...`. Never `pip install` into the project. |

---

## 3. The Message Protocol (THE contract — never break it)

Every agent **listens** for a trigger tag and **emits** an output tag that `@mention`s the next agent. The tags are load-bearing: the Streamlit UI (`detect_message_stage`) and every downstream agent key off them. **Do not rename tags or @mention handles.**

```
UI ──NEW_LOAN_APPLICATION:─→ @IntakeAgent
[1] Intake        ──LOAN_APPLICATION:──→ @DocumentAgent
[2] Document      ──DOC_VERIFICATION:──→ @CreditAgent
[3] Credit        ──CREDIT_ANALYSIS:──→ @FraudAgent
[4] Fraud         ──FRAUD_REPORT:──→ @RiskAgent
[5] Risk          ──RISK_ASSESSMENT:──→ @ComplianceAgent
[6] Compliance    ──COMPLIANCE_CHECK:──→ @DecisionAgent
[7] Decision      ──LOAN_DECISION_READY:──→ @PricingAgent
[8] Pricing       ──PRICING_TERMS:──→ @CommunicationAgent
[9] Communication ──FORMAL_LETTER_READY:──→ Human Gate (no @mention)
Intake on bad data ──INTAKE_ERROR:──→ halts pipeline
```

**Payload format** — plain-text header line with the tag + `@mention`, then a JSON object in a ```json fenced block. The payload is **cumulative**: each agent copies forward all prior fields and adds its own.

**Band routing rules (verified against docs.band.ai):**
- A message only reaches an agent if it **@mentions** that agent. The kickoff message MUST `@mention` the Intake agent or nothing happens.
- Agents post replies by **calling the `band_send_message` tool** (the LangGraph adapter does *not* auto-post the LLM's text). Every agent's system prompt must instruct the model to *call that tool* with the `@NextAgent TAG: <json>` content.

---

## 4. Code Quality (Navnit's standards — enforced)

**Python:**
- Type hints on all function signatures and return types.
- f-strings only (no `.format()` / concatenation).
- `pathlib` over `os.path` for new code.
- PEP 8. `async` where appropriate (agents + Band I/O).
- List/dict comprehensions when readable.
- Handle errors explicitly — **never** silently swallow exceptions (no bare `except:` that returns `None` without logging).

**General:**
- Remove dead code and unused imports before committing.
- Comments explain *why*, not *what*.
- Prefer simple, readable code over clever one-liners.
- Match the style of surrounding code.

---

## 5. Safety Guardrails — CONFIRM before doing any of these

**NEVER:**
- Commit secrets. `.env`, `agent_config.yaml`, and any API key stay **gitignored**. If you generate example values, use obvious placeholders.
- Add any AI tool or bot as a GitHub collaborator or commit co-author. Repo collaborators are the human team only.
- Remove the Human Gate or let any agent auto-finalize / auto-dispatch a letter. Human sign-off is mandatory and is the whole point of Track 3.
- Rename message tags, `@mention` handles, or the agent folder names without updating every consumer (`app.py`, all agents, `preflight.py`).
- Weaken the Compliance Agent's hard blocks — they must override positive credit/risk scores.

**ALWAYS:**
- Run `uv run python preflight.py` after significant changes (it has 94+ checks). Fix FAILs before committing.
- Keep the three demo scenarios (Good → APPROVE, Borderline → COUNTER_OFFER, High Risk → DENY) working.

---

## 6. Branding

The product is **Loan Shark** (two words). The bank entity in letters is **"Loan Shark Financial Services."** The old name was **"LoanPilot"** — there must be **zero** "LoanPilot" references anywhere (preflight checks this).

---

## 7. Git Conventions

- Clear, atomic commits — one logical change each.
- Conventional-commit style prefixes: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`.
- Never commit `.env` / `agent_config.yaml` / keys (see §5).
- Before pushing: run preflight, do a secret sweep, confirm the three demos still work.

---

## 8. Project Map

```
app.py                 Streamlit UI (form + tracker + Human Gate)
band_client.py         Human API client (post + poll room messages)   [see master plan]
shared/parsing.py      Robust JSON extraction + validation + retry      [see master plan]
run_all.py             Launches all 9 agents
preflight.py           94+ system-validation checks
agents/<name>/agent.py 9 agents (intake, document, credit, fraud, risk,
                       compliance, decision, pricing, communication)
schema/messages.py     LEGACY (3-agent era) — being removed/replaced
.streamlit/config.toml Dark theme
docs/                  Plans + specs (start at docs/00_MASTER_PLAN.md)
```

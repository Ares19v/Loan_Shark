<div align="center">

<img src="https://img.shields.io/badge/🦈-LOAN%20SHARK-blue?style=for-the-badge&labelColor=0a0a0f&color=1a6ed8" alt="Loan Shark"/>

# 🦈 LOAN SHARK

### *AI-Powered Loan Processing — 9 Agents. One Decision. Zero Shortcuts.*

[![Python](https://img.shields.io/badge/Python-3.11+-00BCD4?style=flat-square&labelColor=424242&logo=python&logoColor=white)](https://python.org)
[![Band SDK](https://img.shields.io/badge/Band%20SDK-Multi--Agent-00BCD4?style=flat-square&labelColor=424242)](https://app.band.ai)
[![Groq](https://img.shields.io/badge/Groq-llama--3.3--70b-00BCD4?style=flat-square&labelColor=424242)](https://console.groq.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent%20Runtime-00BCD4?style=flat-square&labelColor=424242)](https://langchain-ai.github.io/langgraph/)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-00BCD4?style=flat-square&labelColor=424242&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Hackathon](https://img.shields.io/badge/Band%20of%20Agents-Hackathon%202026-00BCD4?style=flat-square&labelColor=424242)](https://app.band.ai)
[![Track](https://img.shields.io/badge/Track%203-Regulated%20%26%20High--Stakes-00BCD4?style=flat-square&labelColor=424242)]()
[![Team](https://img.shields.io/badge/Team-TrenCoders-4CAF50?style=flat-square&labelColor=673AB7)]()

<br/>

> **"Every loan application that touches our system passes through nine expert AI agents — each with a single job, each accountable for its output, each passing a richer picture forward — before a human makes the call."**

<br/>

</div>

---

## 📖 Table of Contents

- [🎯 The Problem](#-the-problem)
- [💡 The Solution](#-the-solution)
- [🏗️ Architecture Deep Dive](#️-architecture-deep-dive)
- [🤖 Meet the 9 Agents](#-meet-the-9-agents)
- [🔄 Data Flow & Pipeline](#-data-flow--pipeline)
- [🛡️ Compliance & Human-in-the-Loop](#️-compliance--human-in-the-loop)
- [⚡ Why Band Is Non-Negotiable](#-why-band-is-non-negotiable)
- [🚀 Getting Started](#-getting-started)
- [🎬 Demo Scenarios](#-demo-scenarios)
- [🔬 Preflight System Check](#-preflight-system-check)
- [📁 Project Structure](#-project-structure)
- [🛠️ Tech Stack](#️-tech-stack)
- [🏆 Hackathon Track Alignment](#-hackathon-track-alignment)

---

## 🎯 The Problem

Traditional loan processing is **slow, inconsistent, and opaque**.

- A single application can take **3–14 days** to process across multiple departments
- Loan officers manually bounce applications between fraud, credit, compliance, and legal teams
- Each handoff risks **data loss, inconsistency, and undocumented decisions**
- Regulatory requirements demand a full audit trail — yet most systems provide none
- Human bias can enter at any stage, exposing institutions to fair lending violations

**The result:** Applicants wait weeks. Banks lose money on slow pipelines. Compliance teams scramble to reconstruct decisions after the fact.

---

## 💡 The Solution

**Loan Shark** replaces the fragmented, manual handoff chain with a **9-agent AI pipeline** that:

- Processes every application through 9 specialized expert agents in **minutes, not days**
- Passes **structured, enriched context** between each agent via Band's real-time messaging
- Generates a **complete, immutable audit trail** as a natural byproduct of the conversation history
- Enforces **human oversight** at every final decision point — AI recommends, humans decide
- Applies **RBI-compliant regulatory checks** (for Indian lending), with the architecture generalisable globally

The Band room history **is** the audit trail. Every agent handoff, every piece of data enrichment, every flag raised — all timestamped and immutable.

---

## 🏗️ Architecture Deep Dive

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         LOAN SHARK PIPELINE                             │
│                                                                         │
│  Applicant                                                              │
│     │                                                                   │
│     ▼                                                                   │
│  ┌──────────┐                                                           │
│  │ Streamlit│  ←── Beautiful web UI with 3 pre-built demo scenarios     │
│  │   UI     │                                                           │
│  └────┬─────┘                                                           │
│       │ NEW_LOAN_APPLICATION:                                           │
│       │ (posts to Band room via REST API)                               │
│       ▼                                                                 │
│  ╔══════════════╗   ╔══════════════╗   ╔══════════════╗                │
│  ║  [1] INTAKE  ║──▶║  [2] DOCUMENT║──▶║  [3] CREDIT  ║                │
│  ║    AGENT     ║   ║    AGENT     ║   ║    AGENT     ║                │
│  ╚══════════════╝   ╚══════════════╝   ╚══════════════╝                │
│         │                  │                  │                         │
│  Validates &          Doc checks,        Credit grade,                  │
│  structures           consistency,       risk band,                     │
│  application          KYC flags          behaviour                      │
│                                                                         │
│  ╔══════════════╗   ╔══════════════╗   ╔══════════════╗                │
│  ║  [4] FRAUD   ║──▶║  [5] RISK    ║──▶║  [6] COMPLIANCE              │
│  ║    AGENT     ║   ║    AGENT     ║   ║    AGENT     ║                │
│  ╚══════════════╝   ╚══════════════╝   ╚══════════════╝                │
│         │                  │                  │                         │
│  Fraud signals,       DTI ratios,        RBI guidelines,                │
│  identity checks,     employment          exposure limits,              │
│  velocity checks      risk, collateral    fair lending                  │
│                                                                         │
│  ╔══════════════╗   ╔══════════════╗   ╔══════════════╗                │
│  ║  [7] DECISION║──▶║  [8] PRICING ║──▶║  [9] COMMS   ║                │
│  ║    AGENT     ║   ║    AGENT     ║   ║    AGENT     ║                │
│  ╚══════════════╝   ╚══════════════╝   ╚══════════════╝                │
│         │                  │                  │                         │
│  APPROVE /            Exact rate,        Formal sanction                │
│  DENY /               EMI, fees,         or rejection                   │
│  COUNTER_OFFER        tenure terms       letter                         │
│                                                                         │
│                                          │                              │
│                                          ▼                              │
│                               ┌──────────────────────┐                 │
│                               │  👤 HUMAN LOAN OFFICER│                 │
│                               │     REVIEW & SIGN-OFF │                 │
│                               └──────────────────────┘                 │
└─────────────────────────────────────────────────────────────────────────┘
```

**Every arrow is a Band `@mention`**. Every message carries the full structured JSON context from all previous agents — nothing is lost, nothing has to be re-fetched.

---

## 🤖 Meet the 9 Agents

### `[1]` 📥 Intake Agent
**Trigger:** `NEW_LOAN_APPLICATION:`  
**Output:** `LOAN_APPLICATION:` → `@DocumentAgent`

The gatekeeper. Receives raw form data from the Streamlit UI, validates that all required fields are present, sanity-checks values (age ranges, income plausibility, debt ratios), and formats everything into a standardized `LoanApplication` JSON schema. If data is missing or implausible, it fires `INTAKE_ERROR:` and halts the pipeline immediately.

---

### `[2]` 📄 Document Agent
**Trigger:** `LOAN_APPLICATION:`  
**Output:** `DOC_VERIFICATION:` → `@CreditAgent`

Checks whether the applicant's claimed documents are sufficient and internally consistent. Employment type is cross-checked against claimed income stability. Self-employed applicants require different documentation than salaried. It flags inconsistencies (e.g., claiming 10 years employment at age 24) without calling any external database — purely logical consistency checking.

---

### `[3]` 💳 Credit Agent
**Trigger:** `DOC_VERIFICATION:`  
**Output:** `CREDIT_ANALYSIS:` → `@FraudAgent`

Interprets the raw credit score into an actionable credit profile. Maps the score to a credit grade (A+ to F), assesses credit utilization health, identifies risk bands, and determines the maximum loan-to-income ratio permissible for this credit profile. Also flags first-time borrowers (no credit history) with appropriate risk annotations.

---

### `[4]` 🔍 Fraud Agent
**Trigger:** `CREDIT_ANALYSIS:`  
**Output:** `FRAUD_REPORT:` → `@RiskAgent`

The pattern recognizer. Checks for fraud signals including: income-to-loan-amount spikes, mismatched employment claims, synthetic identity indicators, application velocity patterns, and suspicious combinations (unemployed + high loan + no collateral). Returns a `fraud_risk_level` (LOW / MEDIUM / HIGH / CRITICAL) and a list of specific flags with reasoning.

---

### `[5]` 📊 Risk Agent
**Trigger:** `FRAUD_REPORT:`  
**Output:** `RISK_ASSESSMENT:` → `@ComplianceAgent`

The financial modeler. Calculates Debt-to-Income (DTI) ratios before and after the proposed loan, scores employment stability, evaluates collateral quality, and generates a composite `risk_score` (0–100). Also acts as the **data aggregator** — it carries forward all structured fields from agents 1–4 so that downstream agents have complete context without needing to re-read the full conversation history.

---

### `[6]` ⚖️ Compliance Agent
**Trigger:** `RISK_ASSESSMENT:`  
**Output:** `COMPLIANCE_CHECK:` → `@DecisionAgent`

The regulatory guardrail. Validates the application against RBI lending guidelines: maximum DTI thresholds, KYC requirement checks, sector exposure limits, fair lending principle verification (ensures decisions aren't inadvertently discriminatory), and minimum income requirements. If a compliance violation is detected, it can issue a hard block regardless of the credit/risk scores.

---

### `[7]` 🎯 Decision Agent
**Trigger:** `COMPLIANCE_CHECK:`  
**Output:** `LOAN_DECISION_READY:` → `@PricingAgent`

The verdict maker. Applies a deterministic decision matrix to the full context from all 6 upstream agents: APPROVE (all criteria met), DENY (any hard block), or COUNTER_OFFER (approve with modified terms). Generates a full compliance audit note with the specific decision basis, confidence level, and regulatory documentation. This output goes to the human gate AND to the Pricing Agent.

---

### `[8]` 💰 Pricing Agent
**Trigger:** `LOAN_DECISION_READY:`  
**Output:** `PRICING_TERMS:` → `@CommunicationAgent`

The actuary. Calculates exact financial terms: interest rate (within the band approved by the Decision Agent), processing fee percentage, monthly EMI, prepayment penalty structure, and insurance requirements if any. For COUNTER_OFFER decisions, recalculates all terms for the modified loan amount/tenure.

---

### `[9]` ✉️ Communication Agent
**Trigger:** `PRICING_TERMS:`  
**Output:** `FORMAL_LETTER_READY:` → Human Gate

The writer. Drafts the formal, legally-worded letter that will be sent to the applicant — either a **Loan Sanction Letter** (with all approved terms, conditions, next steps, and document submission requirements) or a **Regret Letter** (with denial reasons framed in regulatory language, and guidance on future eligibility). **Does not dispatch autonomously** — the letter goes to the human officer for signature and authorization.

---

## 🔄 Data Flow & Pipeline

Each message in the Band room carries a structured JSON payload in a markdown code fence:

```
NEW_LOAN_APPLICATION:
Applicant: Priya Sharma, Age: 32
Monthly Income: 120000 INR
Employment: salaried at Infosys Ltd (5 years)
Loan Request: 800000 INR for 120 months
Purpose: home
Existing Monthly Debt: 8000 INR
Credit Score: 768
Collateral: Residential property in Bengaluru

Please process this application through the pipeline.
```

Each agent extracts the JSON from the previous message, enriches it, and passes the entire updated payload forward. By Agent 9, the payload contains **every data point from every agent** — a complete, structured application history.

### Message Protocol

| Step | Sender → Receiver | Message Tag | Key Fields Added |
|------|------------------|-------------|-----------------|
| 0 | UI → Intake | `NEW_LOAN_APPLICATION:` | Raw form data |
| 1 | Intake → Document | `LOAN_APPLICATION:` | Validated schema, `application_id` |
| 2 | Document → Credit | `DOC_VERIFICATION:` | `doc_verdict`, `doc_flags[]` |
| 3 | Credit → Fraud | `CREDIT_ANALYSIS:` | `credit_grade`, `max_lti` |
| 4 | Fraud → Risk | `FRAUD_REPORT:` | `fraud_risk_level`, `fraud_flags[]` |
| 5 | Risk → Compliance | `RISK_ASSESSMENT:` | `risk_score`, `dti_ratio`, all prior fields |
| 6 | Compliance → Decision | `COMPLIANCE_CHECK:` | `compliance_verdict`, `violations[]` |
| 7 | Decision → Pricing | `LOAN_DECISION_READY:` | `recommendation`, `approved_amount` |
| 8 | Pricing → Comms | `PRICING_TERMS:` | `interest_rate`, `emi`, `fees` |
| 9 | Comms → Human | `FORMAL_LETTER_READY:` | `letter_body`, full audit trail |

---

## 🛡️ Compliance & Human-in-the-Loop

This system was built with **Track 3 (Regulated & High-Stakes Workflows)** requirements as a first-class constraint, not an afterthought.

### Hard Rules
- ✅ **Human approval required** before any letter is dispatched
- ✅ **No autonomous lending decisions** — AI recommends, humans authorize
- ✅ **Every decision has an audit note** documenting which rule triggered it
- ✅ **Band room history is the complete, timestamped audit trail**
- ✅ **Compliance Agent can issue hard blocks** that override positive risk scores
- ✅ **Fair lending checks** — compliance agent flags if demographics could be inadvertently influencing decisions

### Human Gate (Streamlit UI)
When `FORMAL_LETTER_READY:` is received:
1. The Streamlit dashboard presents the decision summary, key metrics, and the full formal letter preview
2. A human loan officer reviews the AI recommendation + letter
3. They choose **✅ Approve & Finalize** or **❌ Reject / Override**
4. Only after human approval is the application marked as finalized

---

## ⚡ Why Band Is Non-Negotiable

Loan Shark is not simply "an app that uses agents." **Band is the infrastructure** that makes this architecture possible:

| Without Band | With Band |
|-------------|-----------|
| Agents would need a custom message broker | Band provides real-time P2P messaging out of the box |
| Building audit trails requires a separate DB | The room history IS the audit trail — immutable, timestamped |
| Agent coordination needs custom orchestration | `@mention` is the only coordination primitive needed |
| Scaling to 9 agents needs complex plumbing | Each agent is an independent process, Band routes messages |
| Reproducing a decision requires log scraping | Open the Band room. Done. |

The `@mention` protocol is so simple it's elegant: each agent listens, does its job, and hands off. The complexity lives in the agents, not in the messaging layer.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) package manager
- A [Groq](https://console.groq.com) API key (free)
- A [Band](https://app.band.ai) account (use promo code `BANDHACK26` for free pro access)

### Step 1 — Install Dependencies
```bash
uv sync
```

### Step 2 — Configure Environment
```bash
cp .env.example .env
```

Edit `.env`:
```env
GROQ_API_KEY=your-groq-api-key-here
BAND_REST_URL=https://app.band.ai/
BAND_WS_URL=wss://app.band.ai/api/v1/socket/websocket
BAND_ROOM_ID=your-room-id-here
```

### Step 3 — Set Up Band Agents

1. Go to [app.band.ai](https://app.band.ai)
2. Create **9 agents** named: `IntakeAgent`, `DocumentAgent`, `CreditAgent`, `FraudAgent`, `RiskAgent`, `ComplianceAgent`, `DecisionAgent`, `PricingAgent`, `CommunicationAgent`
3. Create one **room** called `LoanShark` and add all 9 agents
4. Copy each agent's **UUID** and **API key** into `agent_config.yaml`:

```yaml
intake:
  agent_id: "your-intake-agent-uuid"
  api_key: "your-intake-agent-api-key"

document:
  agent_id: "your-document-agent-uuid"
  api_key: "your-document-agent-api-key"

# ... (repeat for all 9 agents)
```

### Step 4 — Run Preflight Check
```bash
uv run python preflight.py
```
All 94 checks should pass (or show only Band credential warnings until you fill `agent_config.yaml`).

### Step 5 — Launch All 9 Agents
```bash
# One command — all 9 agents, color-coded output, auto-restart on crash
uv run python run_all.py
```

### Step 6 — Launch the UI
```bash
uv run streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) 🎉

---

## 🎬 Demo Scenarios

The Streamlit UI ships with 3 **pre-built demo scenarios** — click a button, watch the pipeline fire:

| Scenario | Applicant | Profile | Expected Outcome |
|----------|-----------|---------|-----------------|
| ✅ **Good Applicant** | Priya Sharma | Salaried · ₹1.2L/mo · CIBIL 768 · Home loan | `APPROVE` |
| ⚠️ **Borderline** | Arjun Mehta | Self-employed · ₹55K/mo · CIBIL 648 · Vehicle loan | `COUNTER_OFFER` |
| ❌ **High Risk** | Ravi Kumar | Unemployed · ₹30K/mo · No score · No collateral | `DENY` |

These are designed to showcase all three decision paths in a live demo setting.

---

## 🔬 Preflight System Check

Run `preflight.py` before launch to validate every component:

```bash
uv run python preflight.py
```

**94 checks across 10 categories:**

| Category | What It Checks |
|----------|---------------|
| Python & Runtime | Version ≥ 3.11, all 7 packages installed |
| File Structure | All 20 required files present |
| Environment Variables | `.env` populated, no placeholders |
| Agent Config | All 9 agents configured in `agent_config.yaml` |
| Python Syntax | AST-parse all 13 `.py` files |
| Pipeline Chain | Every agent has correct trigger, `@mention`, and output tag |
| Streamlit App | All 9 message types detected, all 9 stages displayed |
| Branding | No stale "LoanPilot" references anywhere |
| API Connectivity | Live Groq API call to `llama-3.3-70b-versatile` |
| SDK Imports | Band SDK, LangGraph, LangChain all importable |

**Exit code 0** = all critical checks pass. **Exit code 1** = fix before launch.

---

## 📁 Project Structure

```
Loan_Shark/
├── agents/
│   ├── intake/agent.py         # Agent 1 — validates & structures applications
│   ├── document/agent.py       # Agent 2 — document completeness & consistency
│   ├── credit/agent.py         # Agent 3 — credit profile & grade analysis
│   ├── fraud/agent.py          # Agent 4 — fraud signals & identity checks
│   ├── risk/agent.py           # Agent 5 — DTI, financial risk scoring
│   ├── compliance/agent.py     # Agent 6 — RBI regulatory compliance
│   ├── decision/agent.py       # Agent 7 — APPROVE / DENY / COUNTER_OFFER
│   ├── pricing/agent.py        # Agent 8 — interest rate, EMI, fees
│   └── communication/agent.py  # Agent 9 — formal sanction/rejection letter
│
├── schema/
│   └── messages.py             # Shared message format constants
│
├── .streamlit/
│   └── config.toml             # Dark theme configuration
│
├── app.py                      # Streamlit UI — application form + pipeline tracker
├── run_all.py                  # Single-command launcher for all 9 agents
├── preflight.py                # 94-check system validation script
├── agent_config.yaml           # Band agent UUIDs and API keys (gitignored)
├── .env.example                # Environment variable template
├── pyproject.toml              # Project metadata and dependencies
├── requirements.txt            # Streamlit Cloud deployment requirements
└── README.md                   # You are here
```

---

## 🛠️ Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| **Agent Orchestration** | [Band SDK](https://app.band.ai) | Real-time P2P messaging, `@mention` routing, immutable audit trail |
| **Agent Runtime** | [LangGraph](https://langchain-ai.github.io/langgraph/) | Stateful agent graphs, structured tool calls |
| **LLM** | [Groq](https://console.groq.com) · `llama-3.3-70b-versatile` | Fast inference, free tier, OpenAI-compatible API |
| **Frontend** | [Streamlit](https://streamlit.io) | Rapid UI, live updates, no frontend boilerplate |
| **Package Manager** | [uv](https://docs.astral.sh/uv/) | Fast, deterministic dependency resolution |
| **Language** | Python 3.11+ | Ecosystem, async support, typing |

---

## 🏆 Hackathon Track Alignment

**Track 3: Regulated & High-Stakes Workflows** — Loan Shark was designed specifically for this track.

| Track Requirement | How Loan Shark Addresses It |
|------------------|---------------------------|
| Human oversight at critical decision points | Human gate before any letter is dispatched; AI cannot finalize independently |
| Complete audit trail for regulatory review | Band room history is the full, timestamped, immutable audit trail |
| Compliance with domain regulations | Dedicated Compliance Agent applies RBI guidelines as a hard gate |
| Structured, reproducible decision-making | Deterministic decision matrix in Decision Agent; same inputs always produce the same output path |
| Multi-agent coordination for complex workflows | 9 specialized agents via Band `@mention` — each with one job, full accountability |
| Error handling and graceful degradation | `INTAKE_ERROR:` halts pipeline; each agent validates its own input before processing |

---

## 👥 Team

**TrenCoders** — *Band of Agents Hackathon 2026*

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with 🦈 by TrenCoders for the Band of Agents Hackathon 2026**

*9 agents. One decision. Zero shortcuts.*

</div>

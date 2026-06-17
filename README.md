# 🦈 Loan Shark

**9-agent AI loan application processing system built for the Band of Agents Hackathon 2026.**

**Track 3: Regulated & High-Stakes Workflows**
**Team: TrenCoders**

---

## What It Does

Loan Shark is a 9-agent pipeline that processes loan applications end-to-end through the Band platform. Every application passes through 9 specialized AI agents — each doing one job, passing structured context to the next — before a human loan officer makes the final call.

```
Applicant submits form (Streamlit UI)
             ↓
[1] Intake Agent        — validates & structures application
             ↓ @DocumentAgent
[2] Document Agent      — checks doc completeness & consistency
             ↓ @CreditAgent
[3] Credit Agent        — interprets credit profile & grade
             ↓ @FraudAgent
[4] Fraud Agent         — detects fraud signals & anomalies
             ↓ @RiskAgent
[5] Risk Agent          — DTI analysis, financial risk scoring
             ↓ @ComplianceAgent
[6] Compliance Agent    — RBI/regulatory check
             ↓ @DecisionAgent
[7] Decision Agent      — APPROVE / DENY / COUNTER_OFFER
             ↓ @PricingAgent
[8] Pricing Agent       — exact rate, EMI, processing fees
             ↓ @CommunicationAgent
[9] Communication Agent — formal sanction/rejection letter
             ↓
Human Loan Officer reviews → approves or rejects → done
```

All coordination happens through Band's real-time messaging. The Band room history IS the audit trail.

---

## Architecture

| Agent | Role | Trigger |
|-------|------|---------|
| IntakeAgent | Validates & structures raw application | `NEW_LOAN_APPLICATION:` |
| DocumentAgent | Doc completeness, consistency checks | `LOAN_APPLICATION:` |
| CreditAgent | Credit grade, behavior, utilization | `DOC_VERIFICATION:` |
| FraudAgent | Fraud signals, synthetic identity, stacking | `CREDIT_ANALYSIS:` |
| RiskAgent | DTI ratio, employment risk, collateral | `FRAUD_REPORT:` |
| ComplianceAgent | RBI guidelines, KYC, exposure limits | `RISK_ASSESSMENT:` |
| DecisionAgent | APPROVE / DENY / COUNTER_OFFER | `COMPLIANCE_CHECK:` |
| PricingAgent | Exact rate, fees, EMI, prepayment terms | `LOAN_DECISION_READY:` |
| CommunicationAgent | Formal letter to applicant | `PRICING_TERMS:` |

**Tech stack:** Band SDK · LangGraph · Groq (llama-3.3-70b-versatile) · Streamlit · Python 3.11+

---

## Setup

### 1. Install dependencies
```bash
uv sync
```

### 2. Configure environment
```bash
cp .env.example .env
# Fill in GROQ_API_KEY and BAND_ROOM_ID
```

### 3. Configure Band agents
Edit `agent_config.yaml` with all 9 agent UUIDs and API keys from app.band.ai

### 4. Run all 9 agents (9 terminal windows)
```bash
uv run python agents/intake/agent.py
uv run python agents/document/agent.py
uv run python agents/credit/agent.py
uv run python agents/fraud/agent.py
uv run python agents/risk/agent.py
uv run python agents/compliance/agent.py
uv run python agents/decision/agent.py
uv run python agents/pricing/agent.py
uv run python agents/communication/agent.py
```

### 5. Launch Streamlit UI
```bash
uv run streamlit run app.py
```

---

## Why Band Is Essential

Each agent can only function with the structured output of the previous agent — the data chain is unbroken and every handoff is visible in the Band room. Remove Band and the pipeline collapses entirely. The room history is the legally required audit trail.

---

## Compliance Notes

- All AI recommendations require human loan officer approval before finalization
- Communication Agent does not dispatch letters autonomously
- Decision Agent generates compliance documentation for every application
- System never makes final lending decisions without a human in the loop

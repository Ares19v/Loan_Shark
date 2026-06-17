"""
COMPLIANCE AGENT — Loan Shark (Agent 6 of 9)

Role: Receives risk assessment result.
- Checks the application against RBI lending guidelines and regulatory requirements
- Verifies KYC completeness, lending limits, and priority sector norms
- Issues compliance verdict before final decision
- Passes forward to Decision Agent
"""

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

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

COMPLIANCE_SYSTEM_PROMPT = """
You are the Compliance Agent in Loan Shark, a 9-agent AI loan processing pipeline.

YOUR ROLE: You are Agent 6. You receive the risk assessment and validate the application
against regulatory lending guidelines. You ensure no loan is approved in violation of
lending norms before it reaches the Decision Agent.

WHEN YOU RECEIVE A MESSAGE CONTAINING "RISK_ASSESSMENT:":
Extract the JSON and perform these regulatory checks:

RBI / LENDING REGULATORY CHECKS:
1. KYC COMPLIANCE:
   - doc_verdict CRITICAL → "KYC incomplete — regulatory block"
   - credit_score null AND loan > 200000 → "Bureau check mandatory for loans above 2L"

2. EXPOSURE LIMITS:
   - total_debt_ratio_post_loan > 60% → "Exceeds recommended exposure limit (60% DTI)"
   - loan_amount > 7500000 AND risk_category HIGH → "Large exposure with high risk — board approval required"

3. FAIR LENDING:
   - If denial would be based solely on unemployment without checking all factors → flag "Ensure fair lending — verify all income sources"
   - fraud_risk_level CRITICAL → "Enhanced Due Diligence (EDD) mandatory per PMLA guidelines"

4. PRIORITY SECTOR:
   - loan_purpose "home" AND loan_amount <= 3500000 → "Eligible for Priority Sector Lending (PSL) classification"
   - loan_purpose "education" → "Check eligibility for government education loan schemes"

5. RISK-BASED PRICING REQUIREMENT:
   - risk_category HIGH or VERY_HIGH → "Risk-based pricing mandatory — cannot offer standard rates"

COMPLIANCE VERDICT:
- COMPLIANT: No regulatory issues
- COMPLIANT_WITH_CONDITIONS: Minor conditions that must be met before disbursement
- NON_COMPLIANT: Regulatory violation — cannot proceed without resolution
- EDD_REQUIRED: Enhanced Due Diligence mandatory before proceeding

RESPOND WITH EXACTLY THIS FORMAT:

@DecisionAgent COMPLIANCE_CHECK:
```json
{
  "application_id": "<same as received>",
  "applicant_name": "<carry forward>",
  "monthly_income": <carry forward>,
  "currency": "<carry forward>",
  "employment_type": "<carry forward>",
  "loan_amount_requested": <carry forward>,
  "loan_purpose": "<carry forward>",
  "loan_tenure_months": <carry forward>,
  "existing_debt_monthly": <carry forward>,
  "credit_score": <carry forward or null>,
  "collateral_offered": "<carry forward or null>",
  "credit_grade": "<carry forward>",
  "credit_recommendation": "<carry forward>",
  "fraud_risk_level": "<carry forward>",
  "clear_to_proceed": <carry forward>,
  "risk_score": <carry forward>,
  "risk_category": "<carry forward>",
  "total_debt_ratio_post_loan": <carry forward>,
  "proposed_emi": <carry forward>,
  "max_eligible_amount": <carry forward>,
  "recommended_tenure_months": <carry forward>,
  "interest_rate_band": "<carry forward>",
  "red_flags": <carry forward array>,
  "positive_factors": <carry forward array>,
  "compliance_issues": ["<issue1>", "<issue2>"],
  "compliance_conditions": ["<condition1>"],
  "priority_sector_eligible": <true|false>,
  "edd_required": <true|false>,
  "compliance_verdict": "<COMPLIANT|COMPLIANT_WITH_CONDITIONS|NON_COMPLIANT|EDD_REQUIRED>",
  "compliance_notes": "<2-3 sentence regulatory summary>"
}
```

IMPORTANT RULES:
- ONLY respond when you see "RISK_ASSESSMENT:" in the message
- ALWAYS @mention DecisionAgent exactly as shown
- Carry forward ALL upstream fields the Decision Agent needs
- NON_COMPLIANT does not automatically mean deny — Decision Agent makes that call
- Do not add commentary outside the JSON block
"""

async def main():
    load_dotenv()
    agent_id, api_key = load_agent_config("compliance")

    llm = ChatOpenAI(
        model="llama-3.3-70b-versatile",
        openai_api_key=os.getenv("GROQ_API_KEY"),
        openai_api_base="https://api.groq.com/openai/v1",
        temperature=0.1,
    )

    adapter = LangGraphAdapter(
        llm=llm,
        checkpointer=InMemorySaver(),
        system_prompt=COMPLIANCE_SYSTEM_PROMPT,
    )

    agent = Agent.create(
        adapter=adapter,
        agent_id=agent_id,
        api_key=api_key,
        ws_url=os.getenv("BAND_WS_URL"),
        rest_url=os.getenv("BAND_REST_URL"),
    )

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [COMPLIANCE] %(message)s", datefmt="%H:%M:%S")
    logger.info("✅ Compliance Agent running...")
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())

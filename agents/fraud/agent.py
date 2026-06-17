"""
FRAUD DETECTION AGENT — Loan Shark (Agent 4 of 9)

Role: Receives credit analysis result.
- Detects fraud signals and application inconsistencies
- Checks for synthetic identity patterns, income inflation, straw borrowing
- Issues fraud risk level and clear-to-proceed flag
- Passes forward to Risk Assessment Agent
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

FRAUD_SYSTEM_PROMPT = """
You are the Fraud Detection Agent in Loan Shark, a 9-agent AI loan processing pipeline.

YOUR ROLE: You are Agent 4. You receive credit analysis results and scan for fraud signals,
application inconsistencies, and high-risk patterns before the financial risk assessment.

WHEN YOU RECEIVE A MESSAGE CONTAINING "CREDIT_ANALYSIS:":
Extract the JSON and check for these fraud signals:

FRAUD SIGNAL CHECKS:
1. INCOME INFLATION:
   - salaried with income > 500000/month AND years_employed < 2 → "Possible income inflation"
   - self_employed with income > 300000/month AND no credit history → "Unverifiable high income"

2. SYNTHETIC IDENTITY:
   - credit_score is null AND loan_amount > 1000000 → "High loan with no credit history — synthetic ID risk"
   - doc_verdict is CRITICAL → "Document anomalies detected — identity verification required"

3. LOAN STACKING:
   - existing_debt_monthly > 0.5 * monthly_income → "High existing debt suggests multiple active loans"
   - existing_debt_monthly > 0 AND credit_score < 600 → "Active debt with poor credit — possible default cascade"

4. MISMATCH SIGNALS:
   - loan_purpose is "personal" AND amount > 2000000 → "Large personal loan — purpose mismatch risk"
   - unemployed AND loan_amount > 500000 → "Large loan with no employment — high fraud risk"

5. VELOCITY INDICATOR:
   - years_employed < 0.5 AND loan_amount > 1000000 → "Large loan early in employment — velocity fraud signal"

FRAUD RISK LEVELS:
- LOW: 0 fraud signals
- MEDIUM: 1-2 fraud signals
- HIGH: 3+ fraud signals OR any synthetic identity signal
- CRITICAL: unemployed + large loan + no credit history

CLEAR TO PROCEED:
- true: fraud_risk_level is LOW or MEDIUM
- false: fraud_risk_level is HIGH or CRITICAL

RESPOND WITH EXACTLY THIS FORMAT:

@RiskAgent FRAUD_REPORT:
```json
{
  "application_id": "<same as received>",
  "applicant_name": "<carry forward>",
  "monthly_income": <carry forward>,
  "currency": "<carry forward>",
  "employment_type": "<carry forward>",
  "employer_name": "<carry forward or null>",
  "years_employed": <carry forward>,
  "loan_amount_requested": <carry forward>,
  "loan_purpose": "<carry forward>",
  "loan_tenure_months": <carry forward>,
  "existing_debt_monthly": <carry forward>,
  "credit_score": <carry forward or null>,
  "collateral_offered": "<carry forward or null>",
  "doc_completeness_score": <carry forward>,
  "doc_verdict": "<carry forward>",
  "credit_grade": "<carry forward>",
  "credit_recommendation": "<carry forward>",
  "fraud_signals": ["<signal1>", "<signal2>"],
  "fraud_risk_level": "<LOW|MEDIUM|HIGH|CRITICAL>",
  "clear_to_proceed": <true|false>,
  "fraud_notes": "<2-3 sentence fraud assessment narrative>"
}
```

IMPORTANT RULES:
- ONLY respond when you see "CREDIT_ANALYSIS:" in the message
- ALWAYS @mention RiskAgent exactly as shown
- clear_to_proceed false does NOT automatically deny — it flags for human scrutiny
- Carry forward ALL upstream fields
- Do not add commentary outside the JSON block
"""

async def main():
    load_dotenv()
    agent_id, api_key = load_agent_config("fraud")

    llm = ChatOpenAI(
        model="llama-3.3-70b-versatile",
        openai_api_key=os.getenv("GROQ_API_KEY"),
        openai_api_base="https://api.groq.com/openai/v1",
        temperature=0.1,
    )

    adapter = LangGraphAdapter(
        llm=llm,
        checkpointer=InMemorySaver(),
        system_prompt=FRAUD_SYSTEM_PROMPT,
    )

    agent = Agent.create(
        adapter=adapter,
        agent_id=agent_id,
        api_key=api_key,
        ws_url=os.getenv("BAND_WS_URL"),
        rest_url=os.getenv("BAND_REST_URL"),
    )

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [FRAUD] %(message)s", datefmt="%H:%M:%S")
    logger.info("✅ Fraud Detection Agent running...")
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())

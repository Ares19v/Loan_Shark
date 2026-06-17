"""
DOCUMENT VERIFICATION AGENT — Loan Shark (Agent 2 of 9)

Role: Receives structured application from Intake Agent.
- Checks document completeness based on employment type
- Cross-checks consistency (income vs employment claims)
- Flags missing or contradictory information
- Passes forward to Credit Analysis Agent
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

DOCUMENT_SYSTEM_PROMPT = """
You are the Document Verification Agent in Loan Shark, a 9-agent AI loan processing pipeline.

YOUR ROLE: You are Agent 2. You receive a validated loan application and check whether
the applicant has provided sufficient documentation and whether the data is internally consistent.

WHEN YOU RECEIVE A MESSAGE CONTAINING "LOAN_APPLICATION:":
Extract the JSON and perform these checks:

REQUIRED DOCS BY EMPLOYMENT TYPE:
- salaried: ["ID proof", "salary slips (3 months)", "bank statement (6 months)", "employment letter"]
- self_employed: ["ID proof", "ITR (2 years)", "bank statement (12 months)", "business registration"]
- business_owner: ["ID proof", "ITR (2 years)", "bank statement (12 months)", "GST registration", "business financials"]
- unemployed: ["ID proof", "bank statement (6 months)", "income source proof"]

CONSISTENCY CHECKS:
- If income > 200000/month AND employment_type is salaried → flag as "Unusually high salary claim — verify"
- If years_employed < 0.5 AND income > 150000 → flag "High income with very short tenure"
- If existing_debt_monthly > monthly_income → CRITICAL flag "Existing debt exceeds income"
- If loan_purpose is "home" AND loan_amount > 10000000 → flag "High-value home loan — enhanced verification needed"
- If credit_score is null → flag "No credit score provided — bureau pull required"
- If collateral_offered is null AND loan_amount > 500000 → flag "Large unsecured loan"

DOC COMPLETENESS SCORE (0-100):
- Start at 100
- -15 for each missing required doc category (estimate from provided info)
- -10 for each consistency flag
- -20 for each CRITICAL flag
(Floor at 0)

RESPOND WITH EXACTLY THIS FORMAT:

@CreditAgent DOC_VERIFICATION:
```json
{
  "application_id": "<same as received>",
  "applicant_name": "<from application>",
  "monthly_income": <from application>,
  "currency": "<from application>",
  "employment_type": "<from application>",
  "employer_name": "<from application or null>",
  "years_employed": <from application>,
  "loan_amount_requested": <from application>,
  "loan_purpose": "<from application>",
  "loan_tenure_months": <from application>,
  "existing_debt_monthly": <from application>,
  "credit_score": <from application or null>,
  "collateral_offered": "<from application or null>",
  "required_docs": ["<doc1>", "<doc2>"],
  "missing_doc_categories": ["<any missing categories>"],
  "consistency_flags": ["<flag1>", "<flag2>"],
  "doc_completeness_score": <integer 0-100>,
  "income_verification_status": "<SUFFICIENT|REQUIRES_VERIFICATION|INSUFFICIENT>",
  "doc_verdict": "<CLEAR|FLAGGED|CRITICAL>"
}
```

DOC VERDICT RULES:
- CLEAR: score >= 70, no CRITICAL flags
- FLAGGED: score 40-69, or any regular flags
- CRITICAL: score < 40, or any CRITICAL flags

IMPORTANT RULES:
- ONLY respond when you see "LOAN_APPLICATION:" in the message
- ALWAYS @mention CreditAgent exactly as shown
- Carry forward ALL original application fields so downstream agents have context
- Do not add commentary outside the JSON block
"""

async def main():
    load_dotenv()
    agent_id, api_key = load_agent_config("document")

    llm = ChatOpenAI(
        model="llama-3.3-70b-versatile",
        openai_api_key=os.getenv("GROQ_API_KEY"),
        openai_api_base="https://api.groq.com/openai/v1",
        temperature=0.1,
    )

    adapter = LangGraphAdapter(
        llm=llm,
        checkpointer=InMemorySaver(),
        system_prompt=DOCUMENT_SYSTEM_PROMPT,
    )

    agent = Agent.create(
        adapter=adapter,
        agent_id=agent_id,
        api_key=api_key,
        ws_url=os.getenv("BAND_WS_URL"),
        rest_url=os.getenv("BAND_REST_URL"),
    )

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [DOCUMENT] %(message)s", datefmt="%H:%M:%S")
    logger.info("✅ Document Verification Agent running...")
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())

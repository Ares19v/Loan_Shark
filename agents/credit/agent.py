"""
CREDIT ANALYSIS AGENT — Loan Shark (Agent 3 of 9)

Role: Receives doc verification result.
- Performs deep credit profile analysis from credit score
- Estimates credit behaviour patterns, utilization, credit age
- Produces credit grade and recommendation
- Passes forward to Fraud Detection Agent
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

CREDIT_SYSTEM_PROMPT = """
You are the Credit Analysis Agent in Loan Shark, a 9-agent AI loan processing pipeline.

YOUR ROLE: You are Agent 3. You receive document verification results and perform
a deep credit profile analysis. You interpret the credit score into actionable credit
intelligence including grade, behavior patterns, and lending recommendation.

WHEN YOU RECEIVE A MESSAGE CONTAINING "DOC_VERIFICATION:":
Extract the JSON and perform credit analysis:

CREDIT GRADE SCALE (based on credit_score):
- 800-900: A+ (Exceptional)
- 750-799: A  (Excellent)
- 700-749: B+ (Good)
- 650-699: B  (Fair)
- 600-649: C  (Poor)
- 300-599: D  (Very Poor)
- null:     U  (Unscored — treat as C for risk purposes)

CREDIT BEHAVIOR INFERENCE (derive from score + employment + income):
- If score >= 750: "Consistent payment history likely. Low credit utilization expected."
- If score 650-749: "Generally responsible borrower. May have occasional late payments."
- If score 600-649: "Some credit stress evident. Possible missed payments in past 2 years."
- If score < 600: "Significant credit distress. Multiple defaults or settlements likely."
- If null: "No credit history available. First-time borrower or limited credit profile."

CREDIT UTILIZATION ESTIMATE:
- Score >= 750: "Estimated < 30% utilization (healthy)"
- Score 650-749: "Estimated 30-60% utilization (moderate)"
- Score < 650: "Estimated > 60% utilization (high stress)"

ESTIMATED CREDIT AGE:
- Infer from age: age < 25 → "Likely < 3 years", 25-35 → "3-8 years", > 35 → "> 8 years"

CREDIT RECOMMENDATION:
- A+, A: PROCEED — strong creditworthiness
- B+: PROCEED_WITH_TERMS — good but price for risk
- B: PROCEED_CAUTIOUSLY — verify income sources
- C: HIGH_RISK — requires collateral or co-applicant
- D: DECLINE_RECOMMENDED — credit history too poor
- U: MANUAL_REVIEW — no credit data, escalate

RESPOND WITH EXACTLY THIS FORMAT:

@FraudAgent CREDIT_ANALYSIS:
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
  "consistency_flags": <carry forward array>,
  "credit_grade": "<A+|A|B+|B|C|D|U>",
  "credit_behavior_summary": "<inferred behavior string>",
  "estimated_credit_utilization": "<utilization string>",
  "estimated_credit_age": "<age string>",
  "credit_recommendation": "<PROCEED|PROCEED_WITH_TERMS|PROCEED_CAUTIOUSLY|HIGH_RISK|DECLINE_RECOMMENDED|MANUAL_REVIEW>",
  "credit_notes": "<2-3 sentence credit narrative>"
}
```

IMPORTANT RULES:
- ONLY respond when you see "DOC_VERIFICATION:" in the message
- ALWAYS @mention FraudAgent exactly as shown
- Carry forward ALL upstream fields so downstream agents have full context
- Do not add commentary outside the JSON block
"""

async def main():
    load_dotenv()
    agent_id, api_key = load_agent_config("credit")

    llm = ChatOpenAI(
        model="llama-3.3-70b-versatile",
        openai_api_key=os.getenv("GROQ_API_KEY"),
        openai_api_base="https://api.groq.com/openai/v1",
        temperature=0.1,
    )

    adapter = LangGraphAdapter(
        llm=llm,
        checkpointer=InMemorySaver(),
        system_prompt=CREDIT_SYSTEM_PROMPT,
    )

    agent = Agent.create(
        adapter=adapter,
        agent_id=agent_id,
        api_key=api_key,
        ws_url=os.getenv("BAND_WS_URL"),
        rest_url=os.getenv("BAND_REST_URL"),
    )

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [CREDIT] %(message)s", datefmt="%H:%M:%S")
    logger.info("✅ Credit Analysis Agent running...")
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())

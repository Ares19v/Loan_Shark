"""
PRICING AGENT — Loan Shark (Agent 8 of 9)

Role: Receives Decision Agent's recommendation.
- Determines exact interest rate, processing fees, prepayment terms
- Structures complete financial terms for the offer
- Passes forward to Communication Agent for letter drafting
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

PRICING_SYSTEM_PROMPT = """
You are the Pricing Agent in Loan Shark, a 9-agent AI loan processing pipeline.

YOUR ROLE: You are Agent 8. You receive the loan decision and determine the precise
financial terms — exact interest rate within the approved band, processing fees,
and special conditions. You only act on APPROVE or COUNTER_OFFER decisions.

WHEN YOU RECEIVE A MESSAGE CONTAINING "LOAN_DECISION_READY:":
Extract the JSON. If recommendation is DENY, pass it through to Communication Agent unchanged.
If APPROVE or COUNTER_OFFER, determine exact pricing:

INTEREST RATE DETERMINATION (within the approved band):
- Credit grade A+ or A: Use LOWER end of interest_rate_band
- Credit grade B+: Use MIDDLE of interest_rate_band
- Credit grade B: Use UPPER end of interest_rate_band
- Credit grade C or below: Use UPPER end + 0.5%
- Priority sector loan: Subtract 0.25% from determined rate
- Collateral provided: Subtract 0.25% from determined rate

PROCESSING FEES (standard market rates):
- Home loan: 0.5% of loan amount (min 5000, max 50000)
- Vehicle loan: 1.0% of loan amount (min 2500, max 25000)
- Education loan: 0% (government directive)
- Personal loan: 1.5% of loan amount (min 1000, max 20000)
- Business loan: 1.0% of loan amount (min 5000, max 50000)

PREPAYMENT TERMS:
- Fixed rate loans: 2% prepayment penalty in first 2 years, nil thereafter
- Floating rate: Nil prepayment penalty (RBI guideline)
(Use floating rate for tenure > 36 months, fixed for <= 36 months)

EMI RECALCULATION:
- Use the exact interest rate determined above
- monthly_rate = annual_rate / 1200
- EMI = P * monthly_rate * (1+monthly_rate)^n / ((1+monthly_rate)^n - 1)

RESPOND WITH EXACTLY THIS FORMAT:

@CommunicationAgent PRICING_TERMS:
```json
{
  "application_id": "<same as received>",
  "applicant_name": "<from decision>",
  "recommendation": "<from decision>",
  "approved_amount": <from decision or null>,
  "approved_tenure_months": <from decision or null>,
  "denial_reasons": <from decision>,
  "counter_offer_notes": <from decision or null>,
  "compliance_verdict": "<carry forward>",
  "priority_sector_eligible": <carry forward>,
  "credit_grade": "<carry forward>",
  "exact_interest_rate": "<e.g. 9.75% p.a. floating>",
  "rate_type": "<fixed|floating>",
  "final_emi": <recalculated float or null if DENY>,
  "processing_fee": <float or null if DENY>,
  "processing_fee_gst": <processing_fee * 0.18 or null>,
  "total_processing_cost": <processing_fee + gst or null>,
  "prepayment_penalty": "<description string>",
  "loan_insurance_recommended": <true|false>,
  "special_conditions": ["<condition1>", "<condition2>"],
  "total_cost_of_loan": <(final_emi * tenure) + processing_cost or null if DENY>,
  "pricing_notes": "<2 sentence explanation of pricing rationale>"
}
```

IMPORTANT RULES:
- ONLY respond when you see "LOAN_DECISION_READY:" in the message
- ALWAYS @mention CommunicationAgent exactly as shown
- If DENY, most financial fields will be null — still pass forward so Communication Agent can draft rejection letter
- loan_insurance_recommended = true if loan_amount > 500000
- Do not add commentary outside the JSON block
"""

async def main():
    load_dotenv()
    agent_id, api_key = load_agent_config("pricing")

    llm = ChatOpenAI(
        model="llama-3.3-70b-versatile",
        openai_api_key=os.getenv("GROQ_API_KEY"),
        openai_api_base="https://api.groq.com/openai/v1",
        temperature=0.1,
    )

    adapter = LangGraphAdapter(
        llm=llm,
        checkpointer=InMemorySaver(),
        system_prompt=PRICING_SYSTEM_PROMPT,
    )

    agent = Agent.create(
        adapter=adapter,
        agent_id=agent_id,
        api_key=api_key,
        ws_url=os.getenv("BAND_WS_URL"),
        rest_url=os.getenv("BAND_REST_URL"),
    )

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [PRICING] %(message)s", datefmt="%H:%M:%S")
    logger.info("✅ Pricing Agent running...")
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())

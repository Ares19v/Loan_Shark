"""
INTAKE AGENT — Loan Shark (Agent 1 of 9)

Role: First agent in the pipeline.
- Receives raw loan application data from the Streamlit UI (via Band room)
- Validates completeness and sanity-checks the data
- Formats it into a structured LoanApplication object
- @mentions DocumentAgent to hand off
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

# ─────────────────────────────────────────────
# SYSTEM PROMPT
# ─────────────────────────────────────────────

INTAKE_SYSTEM_PROMPT = """
You are the Intake Agent in Loan Shark, a 9-agent AI loan processing pipeline.

YOUR ROLE:
You are the first step. You receive raw loan application data submitted by an applicant,
validate it, and pass a clean structured object to the Risk Agent for assessment.

WHEN YOU RECEIVE A MESSAGE TAGGED WITH "NEW_LOAN_APPLICATION:":
1. Parse all the applicant details from the message
2. Validate the data:
   - Are all required fields present?
   - Is income a positive number?
   - Is loan amount reasonable relative to income (flag if > 10x annual income)?
   - Is age between 18 and 70?
   - Is credit score in valid range (300-900) if provided?
   - Is loan tenure between 6 and 360 months?
3. Note any validation flags in validation_notes

THEN RESPOND WITH EXACTLY THIS FORMAT — no other text:

@DocumentAgent LOAN_APPLICATION:
```json
{
  "application_id": "APP-<last4 digits of current unix timestamp>",
  "applicant_name": "<name>",
  "applicant_age": <age as integer>,
  "monthly_income": <income as float>,
  "currency": "<INR or USD>",
  "employment_type": "<salaried|self_employed|business_owner|unemployed>",
  "employer_name": "<employer or null>",
  "years_employed": <years as float>,
  "loan_amount_requested": <amount as float>,
  "loan_purpose": "<purpose>",
  "loan_tenure_months": <months as integer>,
  "existing_debt_monthly": <monthly debt payments as float>,
  "credit_score": <score as integer or null>,
  "collateral_offered": "<description or null>",
  "validation_notes": ["<any flags or empty list>"]
}
```

IMPORTANT RULES:
- ONLY respond when you see "NEW_LOAN_APPLICATION:" in the message
- ALWAYS @mention DocumentAgent exactly as shown above
- Use null for optional fields that are missing
- Do not add any commentary outside the JSON block
- If critical fields are missing (name, income, loan amount), respond with:
  "INTAKE_ERROR: Missing required fields: [list them]. Please resubmit."
- Ignore any other messages not tagged with NEW_LOAN_APPLICATION
"""

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

async def main():
    load_dotenv()

    agent_id, api_key = load_agent_config("intake")

    # Groq is OpenAI-compatible — just change base_url and model
    llm = ChatOpenAI(
        model="llama-3.3-70b-versatile",   # Groq's best free model
        openai_api_key=os.getenv("GROQ_API_KEY"),
        openai_api_base="https://api.groq.com/openai/v1",
        temperature=0.1,
    )

    adapter = LangGraphAdapter(
        llm=llm,
        checkpointer=InMemorySaver(),
        system_prompt=INTAKE_SYSTEM_PROMPT,
    )

    agent = Agent.create(
        adapter=adapter,
        agent_id=agent_id,
        api_key=api_key,
        ws_url=os.getenv("BAND_WS_URL"),
        rest_url=os.getenv("BAND_REST_URL"),
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [INTAKE] %(message)s",
        datefmt="%H:%M:%S",
    )

    logger.info("✅ Intake Agent running — waiting for loan applications...")
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())

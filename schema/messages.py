"""
Shared message schema for all 3 agents.
Every agent reads and writes these structures as @mention messages in Band.
Define this first — all agent logic depends on it.
"""

from dataclasses import dataclass, field
from typing import Literal, Optional
import json


# ─────────────────────────────────────────────
# INTAKE → RISK
# ─────────────────────────────────────────────

@dataclass
class LoanApplication:
    """
    Produced by: Intake Agent
    Consumed by: Risk Agent
    """
    application_id: str
    applicant_name: str
    applicant_age: int
    monthly_income: float           # in INR or USD
    currency: str                   # "INR" or "USD"
    employment_type: Literal[
        "salaried", "self_employed", "business_owner", "unemployed"
    ]
    employer_name: Optional[str]
    years_employed: float
    loan_amount_requested: float
    loan_purpose: str               # e.g. "home", "vehicle", "education", "personal"
    loan_tenure_months: int
    existing_debt_monthly: float    # total existing EMIs/debt payments per month
    credit_score: Optional[int]     # 300–900 range, None if not available
    collateral_offered: Optional[str]
    validation_notes: list[str] = field(default_factory=list)  # any flags from intake

    def to_band_message(self, risk_agent_name: str) -> str:
        data = {
            "application_id": self.application_id,
            "applicant_name": self.applicant_name,
            "applicant_age": self.applicant_age,
            "monthly_income": self.monthly_income,
            "currency": self.currency,
            "employment_type": self.employment_type,
            "employer_name": self.employer_name,
            "years_employed": self.years_employed,
            "loan_amount_requested": self.loan_amount_requested,
            "loan_purpose": self.loan_purpose,
            "loan_tenure_months": self.loan_tenure_months,
            "existing_debt_monthly": self.existing_debt_monthly,
            "credit_score": self.credit_score,
            "collateral_offered": self.collateral_offered,
            "validation_notes": self.validation_notes,
        }
        return (
            f"@{risk_agent_name} LOAN_APPLICATION:\n"
            f"```json\n{json.dumps(data, indent=2)}\n```"
        )


# ─────────────────────────────────────────────
# RISK → DECISION
# ─────────────────────────────────────────────

@dataclass
class RiskAssessment:
    """
    Produced by: Risk Agent
    Consumed by: Decision Agent
    """
    application_id: str
    debt_to_income_ratio: float     # existing_debt / monthly_income (%)
    proposed_emi: float             # estimated monthly EMI for requested loan
    total_debt_ratio_post_loan: float  # (existing + proposed EMI) / income (%)
    risk_score: int                 # 1–100, lower = less risky
    risk_category: Literal["LOW", "MEDIUM", "HIGH", "VERY_HIGH"]
    red_flags: list[str]            # specific issues found
    positive_factors: list[str]     # things in applicant's favour
    max_eligible_amount: float      # what they can safely borrow given income
    recommended_tenure_months: int
    interest_rate_band: str         # e.g. "8.5% – 10.2%"
    requires_collateral: bool
    assessor_notes: str

    def to_band_message(self, decision_agent_name: str) -> str:
        data = {
            "application_id": self.application_id,
            "debt_to_income_ratio": self.debt_to_income_ratio,
            "proposed_emi": self.proposed_emi,
            "total_debt_ratio_post_loan": self.total_debt_ratio_post_loan,
            "risk_score": self.risk_score,
            "risk_category": self.risk_category,
            "red_flags": self.red_flags,
            "positive_factors": self.positive_factors,
            "max_eligible_amount": self.max_eligible_amount,
            "recommended_tenure_months": self.recommended_tenure_months,
            "interest_rate_band": self.interest_rate_band,
            "requires_collateral": self.requires_collateral,
            "assessor_notes": self.assessor_notes,
        }
        return (
            f"@{decision_agent_name} RISK_ASSESSMENT:\n"
            f"```json\n{json.dumps(data, indent=2)}\n```"
        )


# ─────────────────────────────────────────────
# DECISION → HUMAN GATE
# ─────────────────────────────────────────────

@dataclass
class LoanDecision:
    """
    Produced by: Decision Agent
    Consumed by: Human Loan Officer (via Streamlit UI)
    """
    application_id: str
    applicant_name: str
    recommendation: Literal["APPROVE", "DENY", "COUNTER_OFFER"]
    approved_amount: Optional[float]       # None if DENY
    approved_tenure_months: Optional[int]  # None if DENY
    interest_rate: Optional[str]           # None if DENY
    estimated_emi: Optional[float]         # None if DENY
    counter_offer_notes: Optional[str]     # if COUNTER_OFFER, explain the modified terms
    denial_reasons: list[str]              # if DENY, specific reasons
    compliance_notes: str                  # audit trail entry
    risk_category: str
    confidence: Literal["HIGH", "MEDIUM", "LOW"]

    def to_band_message(self) -> str:
        data = {
            "application_id": self.application_id,
            "applicant_name": self.applicant_name,
            "recommendation": self.recommendation,
            "approved_amount": self.approved_amount,
            "approved_tenure_months": self.approved_tenure_months,
            "interest_rate": self.interest_rate,
            "estimated_emi": self.estimated_emi,
            "counter_offer_notes": self.counter_offer_notes,
            "denial_reasons": self.denial_reasons,
            "compliance_notes": self.compliance_notes,
            "risk_category": self.risk_category,
            "confidence": self.confidence,
        }
        return (
            f"LOAN_DECISION_READY:\n"
            f"```json\n{json.dumps(data, indent=2)}\n```\n"
            f"⚠️ Awaiting human loan officer approval before finalizing."
        )


# ─────────────────────────────────────────────
# PARSING HELPERS
# ─────────────────────────────────────────────

def extract_json_from_message(message: str) -> Optional[dict]:
    """Extract JSON block from a Band @mention message."""
    import re
    pattern = r"```json\s*([\s\S]*?)\s*```"
    match = re.search(pattern, message)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return None
    return None


def parse_loan_application(message: str) -> Optional[LoanApplication]:
    """Parse a LOAN_APPLICATION message from the Intake Agent."""
    if "LOAN_APPLICATION:" not in message:
        return None
    data = extract_json_from_message(message)
    if not data:
        return None
    return LoanApplication(**data)


def parse_risk_assessment(message: str) -> Optional[RiskAssessment]:
    """Parse a RISK_ASSESSMENT message from the Risk Agent."""
    if "RISK_ASSESSMENT:" not in message:
        return None
    data = extract_json_from_message(message)
    if not data:
        return None
    return RiskAssessment(**data)


def parse_loan_decision(message: str) -> Optional[LoanDecision]:
    """Parse a LOAN_DECISION_READY message from the Decision Agent."""
    if "LOAN_DECISION_READY:" not in message:
        return None
    data = extract_json_from_message(message)
    if not data:
        return None
    return LoanDecision(**data)

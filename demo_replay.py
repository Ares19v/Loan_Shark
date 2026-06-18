"""
demo_replay.py — Canned mock agent messages and thoughts for simulated replay.
Provides data for the 'good' (APPROVE), 'borderline' (COUNTER_OFFER), and 'highrisk' (DENY) scenarios.
"""

from typing import Any

DEMO_REPLAY_DATA: dict[str, list[dict[str, Any]]] = {
    "good": [
        # INTAKE
        {
            "sender_name": "IntakeAgent",
            "message_type": "thought",
            "content": "I have received a new application for Priya Sharma. The applicant details are complete and all parameters look valid. I will format the loan application and hand it off to the DocumentAgent."
        },
        {
            "sender_name": "IntakeAgent",
            "message_type": "text",
            "content": """@DocumentAgent LOAN_APPLICATION:
```json
{
  "application_id": "APP-284950",
  "applicant_name": "Priya Sharma",
  "applicant_age": 32,
  "monthly_income": 120000.0,
  "currency": "INR",
  "employment_type": "salaried",
  "employer_name": "Infosys Ltd",
  "years_employed": 5.0,
  "loan_amount_requested": 800000.0,
  "loan_purpose": "home",
  "loan_tenure_months": 120,
  "existing_debt_monthly": 8000.0,
  "credit_score": 768,
  "collateral_offered": "Residential property in Bengaluru",
  "validation_notes": []
}
```"""
        },
        # DOCUMENT
        {
            "sender_name": "DocumentAgent",
            "message_type": "thought",
            "content": "Verifying documents for salaried applicant Priya Sharma. Checking salary slips, bank statements, and employment letter. Completeness is 100% and there are no consistency flags."
        },
        {
            "sender_name": "DocumentAgent",
            "message_type": "text",
            "content": """@CreditAgent DOC_VERIFICATION:
```json
{
  "application_id": "APP-284950",
  "applicant_name": "Priya Sharma",
  "monthly_income": 120000.0,
  "currency": "INR",
  "employment_type": "salaried",
  "employer_name": "Infosys Ltd",
  "years_employed": 5.0,
  "loan_amount_requested": 800000.0,
  "loan_purpose": "home",
  "loan_tenure_months": 120,
  "existing_debt_monthly": 8000.0,
  "credit_score": 768,
  "collateral_offered": "Residential property in Bengaluru",
  "required_docs": ["ID proof", "salary slips (3 months)", "bank statement (6 months)", "employment letter"],
  "missing_doc_categories": [],
  "consistency_flags": [],
  "doc_completeness_score": 100,
  "income_verification_status": "SUFFICIENT",
  "doc_verdict": "CLEAR"
}
```"""
        },
        # CREDIT
        {
            "sender_name": "CreditAgent",
            "message_type": "thought",
            "content": "Priya Sharma has an excellent credit score of 768, which maps to credit grade A. Payment history is stable with low utilization. Proceeding with credit analysis."
        },
        {
            "sender_name": "CreditAgent",
            "message_type": "text",
            "content": """@FraudAgent CREDIT_ANALYSIS:
```json
{
  "application_id": "APP-284950",
  "applicant_name": "Priya Sharma",
  "monthly_income": 120000.0,
  "currency": "INR",
  "employment_type": "salaried",
  "employer_name": "Infosys Ltd",
  "years_employed": 5.0,
  "loan_amount_requested": 800000.0,
  "loan_purpose": "home",
  "loan_tenure_months": 120,
  "existing_debt_monthly": 8000.0,
  "credit_score": 768,
  "collateral_offered": "Residential property in Bengaluru",
  "doc_completeness_score": 100,
  "doc_verdict": "CLEAR",
  "consistency_flags": [],
  "credit_grade": "A",
  "credit_behavior_summary": "Consistent payment history likely. Low credit utilization expected.",
  "estimated_credit_utilization": "Estimated < 30% utilization (healthy)",
  "estimated_credit_age": "3-8 years",
  "credit_recommendation": "PROCEED",
  "credit_notes": "Applicant has an established and stable credit profile. CIBIL score is 768, showing excellent payment history and low utilization risk. Recommended to proceed with standard terms."
}
```"""
        },
        # FRAUD
        {
            "sender_name": "FraudAgent",
            "message_type": "thought",
            "content": "Performing fraud and mismatches sweep on Priya Sharma. No flags for income inflation, synthetic ID, or loan stacking detected. Clear to proceed."
        },
        {
            "sender_name": "FraudAgent",
            "message_type": "text",
            "content": """@RiskAgent FRAUD_REPORT:
```json
{
  "application_id": "APP-284950",
  "applicant_name": "Priya Sharma",
  "monthly_income": 120000.0,
  "currency": "INR",
  "employment_type": "salaried",
  "employer_name": "Infosys Ltd",
  "years_employed": 5.0,
  "loan_amount_requested": 800000.0,
  "loan_purpose": "home",
  "loan_tenure_months": 120,
  "existing_debt_monthly": 8000.0,
  "credit_score": 768,
  "collateral_offered": "Residential property in Bengaluru",
  "doc_completeness_score": 100,
  "doc_verdict": "CLEAR",
  "credit_grade": "A",
  "credit_recommendation": "PROCEED",
  "fraud_signals": [],
  "fraud_risk_level": "LOW",
  "clear_to_proceed": true,
  "fraud_notes": "No synthetic identity patterns or suspicious loan velocity indicators. All verified fields align with external credit references. Proceeding with low fraud risk classification."
}
```"""
        },
        # RISK
        {
            "sender_name": "RiskAgent",
            "message_type": "thought",
            "content": "Calculating financial risk metrics for Priya Sharma. Current debt is low. Proposed EMI is 10,750 INR. Debt-to-income ratio remains healthy at 15.6%. Risk score is 20 (LOW)."
        },
        {
            "sender_name": "RiskAgent",
            "message_type": "text",
            "content": """@ComplianceAgent RISK_ASSESSMENT:
```json
{
  "application_id": "APP-284950",
  "applicant_name": "Priya Sharma",
  "monthly_income": 120000.0,
  "currency": "INR",
  "employment_type": "salaried",
  "loan_amount_requested": 800000.0,
  "loan_purpose": "home",
  "loan_tenure_months": 120,
  "existing_debt_monthly": 8000.0,
  "credit_score": 768,
  "collateral_offered": "Residential property in Bengaluru",
  "doc_verdict": "CLEAR",
  "doc_completeness_score": 100,
  "credit_grade": "A",
  "credit_recommendation": "PROCEED",
  "fraud_risk_level": "LOW",
  "clear_to_proceed": true,
  "debt_to_income_ratio": 6.67,
  "proposed_emi": 10982.16,
  "total_debt_ratio_post_loan": 15.82,
  "risk_score": 20,
  "risk_category": "LOW",
  "red_flags": [],
  "positive_factors": ["Excellent credit score", "Long stable employment history", "Low debt-to-income ratio", "Collateral provided reduces lender risk", "Stable salaried income", "Home loan with inherent collateral"],
  "max_eligible_amount": 2400000.0,
  "recommended_tenure_months": 120,
  "interest_rate_band": "8.0% - 9.5%",
  "requires_collateral": false,
  "assessor_notes": "Financial metrics are exceptionally strong. Post-loan total DTI is only 15.82%, well below the 40% threshold. Employment stability is high. Risk is classified as LOW."
}
```"""
        },
        # COMPLIANCE
        {
            "sender_name": "ComplianceAgent",
            "message_type": "thought",
            "content": "Validating application APP-284950 against RBI directives. KYC is complete. DTI is within exposure limits. Priority sector eligibility is active since loan amount is <= 35L and purpose is home loan."
        },
        {
            "sender_name": "ComplianceAgent",
            "message_type": "text",
            "content": """@DecisionAgent COMPLIANCE_CHECK:
```json
{
  "application_id": "APP-284950",
  "applicant_name": "Priya Sharma",
  "monthly_income": 120000.0,
  "currency": "INR",
  "employment_type": "salaried",
  "loan_amount_requested": 800000.0,
  "loan_purpose": "home",
  "loan_tenure_months": 120,
  "existing_debt_monthly": 8000.0,
  "credit_score": 768,
  "collateral_offered": "Residential property in Bengaluru",
  "credit_grade": "A",
  "credit_recommendation": "PROCEED",
  "fraud_risk_level": "LOW",
  "clear_to_proceed": true,
  "risk_score": 20,
  "risk_category": "LOW",
  "total_debt_ratio_post_loan": 15.82,
  "proposed_emi": 10982.16,
  "max_eligible_amount": 2400000.0,
  "recommended_tenure_months": 120,
  "interest_rate_band": "8.0% - 9.5%",
  "red_flags": [],
  "positive_factors": ["Excellent credit score", "Long stable employment history", "Low debt-to-income ratio", "Collateral provided reduces lender risk", "Stable salaried income", "Home loan with inherent collateral"],
  "compliance_issues": [],
  "compliance_conditions": [],
  "priority_sector_eligible": true,
  "edd_required": false,
  "compliance_verdict": "COMPLIANT",
  "compliance_notes": "Application strictly complies with RBI Master Directions on DTI exposure and fair lending norms. Deemed eligible for Priority Sector Lending (PSL)."
}
```"""
        },
        # DECISION
        {
            "sender_name": "DecisionAgent",
            "message_type": "thought",
            "content": "I have evaluated the compliant risk assessment for Priya Sharma. Since all approval rules are met (low risk, DTI <= 50%, no flags), I recommend APPROVAL."
        },
        {
            "sender_name": "DecisionAgent",
            "message_type": "text",
            "content": """@PricingAgent LOAN_DECISION_READY:
```json
{
  "application_id": "APP-284950",
  "applicant_name": "Priya Sharma",
  "recommendation": "APPROVE",
  "approved_amount": 800000.0,
  "approved_tenure_months": 120,
  "interest_rate": "8.5%",
  "estimated_emi": 10982.16,
  "counter_offer_notes": null,
  "denial_reasons": [],
  "compliance_notes": "Generated by Loan Shark AI Decision Agent. Requires human loan officer approval per regulatory guidelines. Decision basis: Approved based on LOW risk score, compliant status, and DTI within limits.",
  "risk_category": "LOW",
  "confidence": "HIGH"
}
```"""
        },
        # PRICING
        {
            "sender_name": "PricingAgent",
            "message_type": "thought",
            "content": "Structuring final terms for approved home loan of Priya Sharma. Adjusting interest rate lower by 0.25% for priority sector and 0.25% for collateral. Recalculating EMI and processing fees."
        },
        {
            "sender_name": "PricingAgent",
            "message_type": "text",
            "content": """@CommunicationAgent PRICING_TERMS:
```json
{
  "application_id": "APP-284950",
  "applicant_name": "Priya Sharma",
  "recommendation": "APPROVE",
  "approved_amount": 800000.0,
  "approved_tenure_months": 120,
  "denial_reasons": [],
  "counter_offer_notes": null,
  "compliance_verdict": "COMPLIANT",
  "priority_sector_eligible": true,
  "credit_grade": "A",
  "exact_interest_rate": "8.00% p.a. floating",
  "rate_type": "floating",
  "final_emi": 9706.0,
  "processing_fee": 5000.0,
  "processing_fee_gst": 900.0,
  "total_processing_cost": 5900.0,
  "prepayment_penalty": "Nil prepayment penalty (floating rate per RBI guidelines)",
  "loan_insurance_recommended": true,
  "special_conditions": ["Submission of original property title deeds", "Home insurance coverage matching loan amount"],
  "total_cost_of_loan": 1170620.0,
  "pricing_notes": "Interest rate set to 8.00% p.a. after applying a 0.25% discount for Priority Sector Lending and a 0.25% discount for collateral. Processing fee set to minimum cap."
}
```"""
        },
        # COMMUNICATION
        {
            "sender_name": "CommunicationAgent",
            "message_type": "thought",
            "content": "Drafting formal sanction letter for Priya Sharma. The letter will summarize all key pricing details and conditions. Handing off to the human gate."
        },
        {
            "sender_name": "CommunicationAgent",
            "message_type": "text",
            "content": """FORMAL_LETTER_READY:
```json
{
  "application_id": "APP-284950",
  "applicant_name": "Priya Sharma",
  "recommendation": "APPROVE",
  "letter_type": "SANCTION",
  "letter_subject": "Loan Sanction Letter — Application APP-284950",
  "letter_body": "LOAN SHARK FINANCIAL SERVICES\\nDate: June 18, 2026\\n\\nTo,\\nPriya Sharma\\nBengaluru\\n\\nSubject: Sanction of Home Loan of Rs 8,00,000/-\\n\\nDear Priya Sharma,\\n\\nWe are pleased to inform you that Loan Shark Financial Services has sanctioned a Home Loan of Rs 8,00,000/- (Rupees Eight Lakhs Only) to you under the following terms and conditions:\\n\\n1. Sanctioned Amount: Rs 8,00,000/-\\n2. Interest Rate: 8.00% p.a. (Floating)\\n3. Tenure: 120 Months (10 Years)\\n4. Monthly EMI: Rs 9,706/-\\n5. Processing Fee: Rs 5,000/- + Rs 900/- (18% GST) = Rs 5,900/-\\n6. Total Cost of Loan: Rs 11,70,620/-\\n7. Prepayment Charges: Nil (per RBI floating rate guidelines)\\n\\nSpecial Conditions:\\n- Submission of original property title deeds prior to disbursement.\\n- Home insurance coverage matching the loan amount must be active.\\n\\nThis sanction letter is generated by Loan Shark AI and requires authorization by a licensed loan officer before it becomes valid.\\n\\nSincerely,\\n[Loan Officer Name to be signed]\\nLoan Shark Financial Services"
}
```"""
        }
    ],
    "borderline": [
        # INTAKE
        {
            "sender_name": "IntakeAgent",
            "message_type": "thought",
            "content": "Received application for Arjun Mehta. Income is 55,000 INR, requested loan is 600,000 INR. The details are complete. Forwarding to DocumentAgent."
        },
        {
            "sender_name": "IntakeAgent",
            "message_type": "text",
            "content": """@DocumentAgent LOAN_APPLICATION:
```json
{
  "application_id": "APP-938204",
  "applicant_name": "Arjun Mehta",
  "applicant_age": 28,
  "monthly_income": 55000.0,
  "currency": "INR",
  "employment_type": "self_employed",
  "employer_name": "Mehta Consulting",
  "years_employed": 1.5,
  "loan_amount_requested": 600000.0,
  "loan_purpose": "vehicle",
  "loan_tenure_months": 60,
  "existing_debt_monthly": 12000.0,
  "credit_score": 648,
  "collateral_offered": null,
  "validation_notes": []
}
```"""
        },
        # DOCUMENT
        {
            "sender_name": "DocumentAgent",
            "message_type": "thought",
            "content": "Verifying self-employed applicant Arjun Mehta. Checked for ITR and bank statements. Score is reduced due to lack of collateral and short self-employment tenure."
        },
        {
            "sender_name": "DocumentAgent",
            "message_type": "text",
            "content": """@CreditAgent DOC_VERIFICATION:
```json
{
  "application_id": "APP-938204",
  "applicant_name": "Arjun Mehta",
  "monthly_income": 55000.0,
  "currency": "INR",
  "employment_type": "self_employed",
  "employer_name": "Mehta Consulting",
  "years_employed": 1.5,
  "loan_amount_requested": 600000.0,
  "loan_purpose": "vehicle",
  "loan_tenure_months": 60,
  "existing_debt_monthly": 12000.0,
  "credit_score": 648,
  "collateral_offered": null,
  "required_docs": ["ID proof", "ITR (2 years)", "bank statement (12 months)", "business registration"],
  "missing_doc_categories": [],
  "consistency_flags": ["Large unsecured loan (amount > 5L without collateral)"],
  "doc_completeness_score": 90,
  "income_verification_status": "REQUIRES_VERIFICATION",
  "doc_verdict": "FLAGGED"
}
```"""
        },
        # CREDIT
        {
            "sender_name": "CreditAgent",
            "message_type": "thought",
            "content": "CIBIL score is 648, which falls in Credit Grade B (Fair). Moderate credit risk. Recommending to proceed cautiously with risk-pricing terms."
        },
        {
            "sender_name": "CreditAgent",
            "message_type": "text",
            "content": """@FraudAgent CREDIT_ANALYSIS:
```json
{
  "application_id": "APP-938204",
  "applicant_name": "Arjun Mehta",
  "monthly_income": 55000.0,
  "currency": "INR",
  "employment_type": "self_employed",
  "employer_name": "Mehta Consulting",
  "years_employed": 1.5,
  "loan_amount_requested": 600000.0,
  "loan_purpose": "vehicle",
  "loan_tenure_months": 60,
  "existing_debt_monthly": 12000.0,
  "credit_score": 648,
  "collateral_offered": null,
  "doc_completeness_score": 90,
  "doc_verdict": "FLAGGED",
  "consistency_flags": ["Large unsecured loan (amount > 5L without collateral)"],
  "credit_grade": "B",
  "credit_behavior_summary": "Generally responsible borrower. May have occasional late payments.",
  "estimated_credit_utilization": "Estimated > 60% utilization (high stress)",
  "estimated_credit_age": "3-8 years",
  "credit_recommendation": "PROCEED_CAUTIOUSLY",
  "credit_notes": "Applicant credit score is 648, indicating fair creditworthiness. There is high estimated utilization of existing credit lines. Income verification is crucial."
}
```"""
        },
        # FRAUD
        {
            "sender_name": "FraudAgent",
            "message_type": "thought",
            "content": "Running fraud diagnostics on Arjun Mehta. Existing debt ratio is 21.8%, which is high but doesn't trigger critical stacking flags. No synthetic ID signals. Fraud risk: MEDIUM."
        },
        {
            "sender_name": "FraudAgent",
            "message_type": "text",
            "content": """@RiskAgent FRAUD_REPORT:
```json
{
  "application_id": "APP-938204",
  "applicant_name": "Arjun Mehta",
  "monthly_income": 55000.0,
  "currency": "INR",
  "employment_type": "self_employed",
  "employer_name": "Mehta Consulting",
  "years_employed": 1.5,
  "loan_amount_requested": 600000.0,
  "loan_purpose": "vehicle",
  "loan_tenure_months": 60,
  "existing_debt_monthly": 12000.0,
  "credit_score": 648,
  "collateral_offered": null,
  "doc_completeness_score": 90,
  "doc_verdict": "FLAGGED",
  "credit_grade": "B",
  "credit_recommendation": "PROCEED_CAUTIOUSLY",
  "fraud_signals": ["High existing debt ratio relative to self-employed income"],
  "fraud_risk_level": "MEDIUM",
  "clear_to_proceed": true,
  "fraud_notes": "No severe identity discrepancies. High debt ratio checked. Proceeding with caution due to self-employed status and fair credit profile."
}
```"""
        },
        # RISK
        {
            "sender_name": "RiskAgent",
            "message_type": "thought",
            "content": "Calculating DTI for Arjun Mehta. Existing debt is 12,000 INR. Proposed vehicle loan EMI is 13,010.35 INR. Total post-loan DTI ratio is 45.47%, which exceeds the 40% threshold. Max eligible loan is 400,000 INR."
        },
        {
            "sender_name": "RiskAgent",
            "message_type": "text",
            "content": """@ComplianceAgent RISK_ASSESSMENT:
```json
{
  "application_id": "APP-938204",
  "applicant_name": "Arjun Mehta",
  "monthly_income": 55000.0,
  "currency": "INR",
  "employment_type": "self_employed",
  "loan_amount_requested": 600000.0,
  "loan_purpose": "vehicle",
  "loan_tenure_months": 60,
  "existing_debt_monthly": 12000.0,
  "credit_score": 648,
  "collateral_offered": null,
  "doc_verdict": "FLAGGED",
  "doc_completeness_score": 90,
  "credit_grade": "B",
  "credit_recommendation": "PROCEED_CAUTIOUSLY",
  "fraud_risk_level": "MEDIUM",
  "clear_to_proceed": true,
  "debt_to_income_ratio": 21.82,
  "proposed_emi": 13010.35,
  "total_debt_ratio_post_loan": 45.47,
  "risk_score": 55,
  "risk_category": "HIGH",
  "red_flags": ["Total debt ratio post-loan > 40%", "Large unsecured loan"],
  "positive_factors": ["Moderate DTI prior to loan"],
  "max_eligible_amount": 400000.0,
  "recommended_tenure_months": 60,
  "interest_rate_band": "11.0% - 14.0%",
  "requires_collateral": true,
  "assessor_notes": "Post-loan DTI of 45.47% exceeds the standard 40% safety margin for self-employed individuals. Credit grade is B. Recommending a counter-offer at Rs 4,00,000 to keep post-loan DTI below 35%."
}
```"""
        },
        # COMPLIANCE
        {
            "sender_name": "ComplianceAgent",
            "message_type": "thought",
            "content": "Assessing application compliance. Risk category is HIGH, requiring risk-based pricing. DTI exposure limit checked. Verdict: COMPLIANT_WITH_CONDITIONS (need hypothecation of vehicle)."
        },
        {
            "sender_name": "ComplianceAgent",
            "message_type": "text",
            "content": """@DecisionAgent COMPLIANCE_CHECK:
```json
{
  "application_id": "APP-938204",
  "applicant_name": "Arjun Mehta",
  "monthly_income": 55000.0,
  "currency": "INR",
  "employment_type": "self_employed",
  "employer_name": "Mehta Consulting",
  "years_employed": 1.5,
  "loan_amount_requested": 600000.0,
  "loan_purpose": "vehicle",
  "loan_tenure_months": 60,
  "existing_debt_monthly": 12000.0,
  "credit_score": 648,
  "collateral_offered": null,
  "credit_grade": "B",
  "credit_recommendation": "PROCEED_CAUTIOUSLY",
  "fraud_risk_level": "MEDIUM",
  "clear_to_proceed": true,
  "risk_score": 55,
  "risk_category": "HIGH",
  "total_debt_ratio_post_loan": 45.47,
  "proposed_emi": 13010.35,
  "max_eligible_amount": 400000.0,
  "recommended_tenure_months": 60,
  "interest_rate_band": "11.0% - 14.0%",
  "red_flags": ["Total debt ratio post-loan > 40%", "Large unsecured loan"],
  "positive_factors": ["Moderate DTI prior to loan"],
  "compliance_issues": ["High DTI post-loan at requested amount"],
  "compliance_conditions": ["Hypothecation of the vehicle to be purchased", "Submission of latest GST filing certificates"],
  "priority_sector_eligible": false,
  "edd_required": false,
  "compliance_verdict": "COMPLIANT_WITH_CONDITIONS",
  "compliance_notes": "Complies with general credit exposure rules provided exposure is minimized. Risk-based pricing is mandatory. Hypothecation of asset is a regulatory prerequisite."
}
```"""
        },
        # DECISION
        {
            "sender_name": "DecisionAgent",
            "message_type": "thought",
            "content": "Requested loan of 600,000 exceeds DTI limit, but applicant qualifies for a counter-offer at 400,000. Proposing COUNTER_OFFER."
        },
        {
            "sender_name": "DecisionAgent",
            "message_type": "text",
            "content": """@PricingAgent LOAN_DECISION_READY:
```json
{
  "application_id": "APP-938204",
  "applicant_name": "Arjun Mehta",
  "recommendation": "COUNTER_OFFER",
  "approved_amount": 400000.0,
  "approved_tenure_months": 60,
  "interest_rate": "12.5%",
  "estimated_emi": 9005.12,
  "counter_offer_notes": "Reduced amount to keep DTI within safety margin of 35% for self-employed professionals.",
  "denial_reasons": [],
  "compliance_notes": "Generated by Loan Shark AI Decision Agent. Requires human loan officer approval. Decision basis: Proposed counter-offer as DTI at Rs 6L was excessive but Rs 4L keeps the borrower credit-worthy.",
  "risk_category": "HIGH",
  "confidence": "MEDIUM"
}
```"""
        },
        # PRICING
        {
            "sender_name": "PricingAgent",
            "message_type": "thought",
            "content": "Applying pricing rules for COUNTER_OFFER. Credit grade is B, mapping to the upper end of the interest rate band (12.5% p.a.). Recalculating processing fees and EMIs."
        },
        {
            "sender_name": "PricingAgent",
            "message_type": "text",
            "content": """@CommunicationAgent PRICING_TERMS:
```json
{
  "application_id": "APP-938204",
  "applicant_name": "Arjun Mehta",
  "recommendation": "COUNTER_OFFER",
  "approved_amount": 400000.0,
  "approved_tenure_months": 60,
  "denial_reasons": [],
  "counter_offer_notes": "Reduced amount to keep DTI within safety margin of 35% for self-employed professionals.",
  "compliance_verdict": "COMPLIANT_WITH_CONDITIONS",
  "priority_sector_eligible": false,
  "credit_grade": "B",
  "exact_interest_rate": "12.50% p.a. fixed",
  "rate_type": "fixed",
  "final_emi": 9005.0,
  "processing_fee": 4000.0,
  "processing_fee_gst": 720.0,
  "total_processing_cost": 4720.0,
  "prepayment_penalty": "2% penalty in first 2 years, nil thereafter (fixed rate)",
  "loan_insurance_recommended": false,
  "special_conditions": ["Hypothecation of vehicle in bank's favor", "Submission of two years IT returns"],
  "total_cost_of_loan": 545020.0,
  "pricing_notes": "Vehicle loan processing fee set at 1.0% of the counter-offered amount. Rate of 12.50% represents the upper bound of the HIGH band due to credit grade B."
}
```"""
        },
        # COMMUNICATION
        {
            "sender_name": "CommunicationAgent",
            "message_type": "thought",
            "content": "Drafting counter-offer sanction letter summarizing the modified terms for Arjun Mehta. Handing off to the human gate."
        },
        {
            "sender_name": "CommunicationAgent",
            "message_type": "text",
            "content": """FORMAL_LETTER_READY:
```json
{
  "application_id": "APP-938204",
  "applicant_name": "Arjun Mehta",
  "recommendation": "COUNTER_OFFER",
  "letter_type": "SANCTION",
  "letter_subject": "Proposed Counter-Offer for Vehicle Loan — Application APP-938204",
  "letter_body": "LOAN SHARK FINANCIAL SERVICES\\nDate: June 18, 2026\\n\\nTo,\\nArjun Mehta\\nMumbai\\n\\nSubject: Counter-Offer for Vehicle Loan of Rs 4,00,000/-\\n\\nDear Arjun Mehta,\\n\\nThank you for choosing Loan Shark Financial Services. We have evaluated your application APP-938204. While we are unable to sanction your requested amount of Rs 6,00,000 due to exposure limits, we are pleased to propose a Counter-Offer of Rs 4,00,000/- (Rupees Four Lakhs Only) under the following structured terms:\\n\\n1. Sanctioned Amount: Rs 4,00,000/-\\n2. Interest Rate: 12.50% p.a. (Fixed)\\n3. Tenure: 60 Months (5 Years)\\n4. Monthly EMI: Rs 9,005/-\\n5. Processing Fee: Rs 4,000/- + Rs 720/- (18% GST) = Rs 4,720/-\\n6. Total Cost of Loan: Rs 5,45,020/-\\n7. Prepayment Charges: 2% in first 2 years, nil thereafter\\n\\nSpecial Conditions:\\n- Hypothecation of vehicle purchased in bank's favor.\\n- Submission of last 2 years audited ITR certificates.\\n\\nThis proposed offer is subject to your acceptance and final officer signature.\\n\\nSincerely,\\n[Loan Officer Name to be signed]\\nLoan Shark Financial Services"
}
```"""
        }
    ],
    "highrisk": [
        # INTAKE
        {
            "sender_name": "IntakeAgent",
            "message_type": "thought",
            "content": "I have received a new application for Ravi Kumar. The applicant age is 45, employment status is unemployed. High risk profile, but I will format and pass to DocumentAgent."
        },
        {
            "sender_name": "IntakeAgent",
            "message_type": "text",
            "content": """@DocumentAgent LOAN_APPLICATION:
```json
{
  "application_id": "APP-482019",
  "applicant_name": "Ravi Kumar",
  "applicant_age": 45,
  "monthly_income": 30000.0,
  "currency": "INR",
  "employment_type": "unemployed",
  "employer_name": null,
  "years_employed": 0.0,
  "loan_amount_requested": 500000.0,
  "loan_purpose": "personal",
  "loan_tenure_months": 36,
  "existing_debt_monthly": 18000.0,
  "credit_score": null,
  "collateral_offered": null,
  "validation_notes": ["Applicant lists unemployed employment status"]
}
```"""
        },
        # DOCUMENT
        {
            "sender_name": "DocumentAgent",
            "message_type": "thought",
            "content": "Verifying unemployed applicant Ravi Kumar. Bank statement provided is 6 months, but income source proof is missing. Credit score is also missing. Verdict is CRITICAL."
        },
        {
            "sender_name": "DocumentAgent",
            "message_type": "text",
            "content": """@CreditAgent DOC_VERIFICATION:
```json
{
  "application_id": "APP-482019",
  "applicant_name": "Ravi Kumar",
  "monthly_income": 30000.0,
  "currency": "INR",
  "employment_type": "unemployed",
  "employer_name": null,
  "years_employed": 0.0,
  "loan_amount_requested": 500000.0,
  "loan_purpose": "personal",
  "loan_tenure_months": 36,
  "existing_debt_monthly": 18000.0,
  "credit_score": null,
  "collateral_offered": null,
  "required_docs": ["ID proof", "bank statement (6 months)", "income source proof"],
  "missing_doc_categories": ["income source proof"],
  "consistency_flags": ["Unemployed with no collateral", "No credit score provided — bureau pull required"],
  "doc_completeness_score": 35,
  "income_verification_status": "INSUFFICIENT",
  "doc_verdict": "CRITICAL"
}
```"""
        },
        # CREDIT
        {
            "sender_name": "CreditAgent",
            "message_type": "thought",
            "content": "No credit history is available for applicant Ravi Kumar. The grade is U (Unscored). Recommend manual review or decline due to other risk factors."
        },
        {
            "sender_name": "CreditAgent",
            "message_type": "text",
            "content": """@FraudAgent CREDIT_ANALYSIS:
```json
{
  "application_id": "APP-482019",
  "applicant_name": "Ravi Kumar",
  "monthly_income": 30000.0,
  "currency": "INR",
  "employment_type": "unemployed",
  "employer_name": null,
  "years_employed": 0.0,
  "loan_amount_requested": 500000.0,
  "loan_purpose": "personal",
  "loan_tenure_months": 36,
  "existing_debt_monthly": 18000.0,
  "credit_score": null,
  "collateral_offered": null,
  "doc_completeness_score": 35,
  "doc_verdict": "CRITICAL",
  "consistency_flags": ["Unemployed with no collateral", "No credit score provided — bureau pull required"],
  "credit_grade": "U",
  "credit_behavior_summary": "No credit history available. First-time borrower or limited credit profile.",
  "estimated_credit_utilization": "Estimated > 60% utilization (high stress)",
  "estimated_credit_age": "Likely < 3 years",
  "credit_recommendation": "MANUAL_REVIEW",
  "credit_notes": "Unscored borrower. Credit history is empty. Combining this with unemployment status represents an extremely high risk profile."
}
```"""
        },
        # FRAUD
        {
            "sender_name": "FraudAgent",
            "message_type": "thought",
            "content": "Analyzing fraud indicators. Ravi Kumar is unemployed, requested 5L with no credit score or collateral. This triggers a critical mismatch / identity check signal. Fraud level: CRITICAL."
        },
        {
            "sender_name": "FraudAgent",
            "message_type": "text",
            "content": """@RiskAgent FRAUD_REPORT:
```json
{
  "application_id": "APP-482019",
  "applicant_name": "Ravi Kumar",
  "monthly_income": 30000.0,
  "currency": "INR",
  "employment_type": "unemployed",
  "employer_name": null,
  "years_employed": 0.0,
  "loan_amount_requested": 500000.0,
  "loan_purpose": "personal",
  "loan_tenure_months": 36,
  "existing_debt_monthly": 18000.0,
  "credit_score": null,
  "collateral_offered": null,
  "doc_completeness_score": 35,
  "doc_verdict": "CRITICAL",
  "credit_grade": "U",
  "credit_recommendation": "MANUAL_REVIEW",
  "fraud_signals": ["Large loan with no employment — high fraud risk", "Identity mismatch checks required due to missing credit bureau file"],
  "fraud_risk_level": "CRITICAL",
  "clear_to_proceed": false,
  "fraud_notes": "Identity validation failed to verify active income streams. Risk of synthetic profile or high-probability default. Fraud score is critical."
}
```"""
        },
        # RISK
        {
            "sender_name": "RiskAgent",
            "message_type": "thought",
            "content": "Calculating DTI for Ravi Kumar. Existing debt payments are 18,000 INR (DTI is 60.0%). Proposed EMI is 16,335 INR. Post-loan DTI ratio is 114.45%! Risk category: VERY_HIGH. Max eligible amount is 0."
        },
        {
            "sender_name": "RiskAgent",
            "message_type": "text",
            "content": """@ComplianceAgent RISK_ASSESSMENT:
```json
{
  "application_id": "APP-482019",
  "applicant_name": "Ravi Kumar",
  "monthly_income": 30000.0,
  "currency": "INR",
  "employment_type": "unemployed",
  "loan_amount_requested": 500000.0,
  "loan_purpose": "personal",
  "loan_tenure_months": 36,
  "existing_debt_monthly": 18000.0,
  "credit_score": null,
  "collateral_offered": null,
  "doc_verdict": "CRITICAL",
  "doc_completeness_score": 35,
  "credit_grade": "U",
  "credit_recommendation": "MANUAL_REVIEW",
  "fraud_risk_level": "CRITICAL",
  "clear_to_proceed": false,
  "debt_to_income_ratio": 60.00,
  "proposed_emi": 16335.0,
  "total_debt_ratio_post_loan": 114.45,
  "risk_score": 95,
  "risk_category": "VERY_HIGH",
  "red_flags": ["Total debt ratio post-loan > 50%", "No current employment", "Current debt burden already high (>40% of income)"],
  "positive_factors": [],
  "max_eligible_amount": 0.0,
  "recommended_tenure_months": 36,
  "interest_rate_band": "14.0% - 18.0%",
  "requires_collateral": true,
  "assessor_notes": "DTI post-loan would be 114.45% of monthly income. The applicant is unemployed with high pre-existing debts. Risk score is 95, very high hazard."
}
```"""
        },
        # COMPLIANCE
        {
            "sender_name": "ComplianceAgent",
            "message_type": "thought",
            "content": "Checking compliance directives. doc_verdict is CRITICAL, resulting in a KYC incomplete block. Fraud risk is CRITICAL, triggering a PMLA P0 regulatory block. Verdict: NON_COMPLIANT."
        },
        {
            "sender_name": "ComplianceAgent",
            "message_type": "text",
            "content": """@DecisionAgent COMPLIANCE_CHECK:
```json
{
  "application_id": "APP-482019",
  "applicant_name": "Ravi Kumar",
  "monthly_income": 30000.0,
  "currency": "INR",
  "employment_type": "unemployed",
  "loan_amount_requested": 500000.0,
  "loan_purpose": "personal",
  "loan_tenure_months": 36,
  "existing_debt_monthly": 18000.0,
  "credit_score": null,
  "collateral_offered": null,
  "credit_grade": "U",
  "credit_recommendation": "MANUAL_REVIEW",
  "fraud_risk_level": "CRITICAL",
  "clear_to_proceed": false,
  "risk_score": 95,
  "risk_category": "VERY_HIGH",
  "total_debt_ratio_post_loan": 114.45,
  "proposed_emi": 16335.0,
  "max_eligible_amount": 0.0,
  "recommended_tenure_months": 36,
  "interest_rate_band": "14.0% - 18.0%",
  "red_flags": ["Total debt ratio post-loan > 50%", "No current employment", "Current debt burden already high (>40% of income)"],
  "positive_factors": [],
  "compliance_issues": ["KYC incomplete — regulatory block", "Exceeds exposure limit (DTI > 60%)", "Enhanced Due Diligence mandatory per PMLA guidelines"],
  "compliance_conditions": [],
  "priority_sector_eligible": false,
  "edd_required": true,
  "compliance_verdict": "NON_COMPLIANT",
  "compliance_notes": "Application fails critical RBI compliance tests. DTI limit is exceeded, KYC is incomplete, and severe AML/PMLA fraud warning blocks lending."
}
```"""
        },
        # DECISION
        {
            "sender_name": "DecisionAgent",
            "message_type": "thought",
            "content": "Compliance verdict is NON_COMPLIANT, risk score is 95, and applicant is unemployed. Decision rule 3 dictates a DENY recommendation."
        },
        {
            "sender_name": "DecisionAgent",
            "message_type": "text",
            "content": """@PricingAgent LOAN_DECISION_READY:
```json
{
  "application_id": "APP-482019",
  "applicant_name": "Ravi Kumar",
  "recommendation": "DENY",
  "approved_amount": null,
  "approved_tenure_months": null,
  "interest_rate": null,
  "estimated_emi": null,
  "counter_offer_notes": null,
  "denial_reasons": ["KYC verification blocked due to critical document anomalies", "Applicant is unemployed with zero collateral offered", "Post-loan DTI (114%) exceeds statutory limits", "Enhanced Due Diligence flag triggered per PMLA guidelines"],
  "compliance_notes": "Generated by Loan Shark AI Decision Agent. Requires human loan officer approval. Decision basis: Hard DENY recommendation. The application fails multiple credit and regulatory rules.",
  "risk_category": "VERY_HIGH",
  "confidence": "HIGH"
}
```"""
        },
        # PRICING
        {
            "sender_name": "PricingAgent",
            "message_type": "thought",
            "content": "Lending recommendation is DENY. Passing through all decision fields unchanged as financial terms are not applicable."
        },
        {
            "sender_name": "PricingAgent",
            "message_type": "text",
            "content": """@CommunicationAgent PRICING_TERMS:
```json
{
  "application_id": "APP-482019",
  "applicant_name": "Ravi Kumar",
  "recommendation": "DENY",
  "approved_amount": null,
  "approved_tenure_months": null,
  "denial_reasons": ["KYC verification blocked due to critical document anomalies", "Applicant is unemployed with zero collateral offered", "Post-loan DTI (114%) exceeds statutory limits", "Enhanced Due Diligence flag triggered per PMLA guidelines"],
  "counter_offer_notes": null,
  "compliance_verdict": "NON_COMPLIANT",
  "priority_sector_eligible": false,
  "credit_grade": "U",
  "exact_interest_rate": null,
  "rate_type": null,
  "final_emi": null,
  "processing_fee": null,
  "processing_fee_gst": null,
  "total_processing_cost": null,
  "prepayment_penalty": null,
  "loan_insurance_recommended": false,
  "special_conditions": [],
  "total_cost_of_loan": null,
  "pricing_notes": "Lending terms are not applicable. Recommendation is DENY."
}
```"""
        },
        # COMMUNICATION
        {
            "sender_name": "CommunicationAgent",
            "message_type": "thought",
            "content": "Drafting professional regret letter for Ravi Kumar. Citing general reasons without violating confidentiality. Handing off to the human gate."
        },
        {
            "sender_name": "CommunicationAgent",
            "message_type": "text",
            "content": """FORMAL_LETTER_READY:
```json
{
  "application_id": "APP-482019",
  "applicant_name": "Ravi Kumar",
  "recommendation": "DENY",
  "letter_type": "REGRET",
  "letter_subject": "Loan Application Status — Application APP-482019",
  "letter_body": "LOAN SHARK FINANCIAL SERVICES\\nDate: June 18, 2026\\n\\nTo,\\nRavi Kumar\\n\\nSubject: Loan Application APP-482019\\n\\nDear Ravi Kumar,\\n\\nThank you for your interest in Loan Shark Financial Services. We appreciate the time you took to submit your loan application APP-482019.\\n\\nWe regret to inform you that, after careful review of your application details against our standard credit guidelines and regulatory criteria, we are unable to approve your request at this time.\\n\\nOur decision was primarily guided by exposure guidelines and standard risk thresholds. This decision does not reflect upon your character or personal integrity.\\n\\nWe encourage you to re-apply after a period of 6 months if your employment status stabilizes or if you are able to offer suitable collateral to reduce exposure risk.\\n\\nThank you for your understanding. We wish you success in your financial endeavors.\\n\\nSincerely,\\n[Loan Officer Name to be signed]\\nLoan Shark Financial Services"
}
```"""
        }
    ]
}

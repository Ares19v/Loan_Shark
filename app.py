"""
Loan Shark — Streamlit Frontend
The required "working demo URL" for hackathon submission.

What this does:
- Loan application form for applicant to fill in
- Submits the application to the Band room (triggers the 3-agent pipeline)
- Live feed showing agent messages from the Band room in real-time
- Human loan officer approval interface once Decision Agent posts its verdict
"""

import streamlit as st
import os
import time
from datetime import datetime
from typing import Any
from dotenv import load_dotenv

from band_client import (
    post_message,
    poll_messages,
    now_iso,
    BandClientError,
    is_configured,
    missing_config,
)
from shared.parsing import extract_json_from_message

load_dotenv()

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Loan Shark — AI Loan Processing",
    page_icon="🦈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.main {
    background: #0a0a0f;
    color: #e8e8f0;
}

.stApp {
    background: linear-gradient(135deg, #0a0a0f 0%, #0d1117 50%, #0a0f1a 100%);
}

/* Header */
.lp-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border: 1px solid rgba(99, 179, 237, 0.2);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    gap: 1.5rem;
}

.lp-title {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #63b3ed, #90cdf4, #bee3f8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}

.lp-subtitle {
    color: #a0aec0;
    font-size: 0.9rem;
    margin: 0;
    margin-top: 0.25rem;
}

/* Status badges */
.badge-processing {
    background: rgba(246, 173, 85, 0.15);
    border: 1px solid rgba(246, 173, 85, 0.4);
    color: #f6ad55;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-block;
}

.badge-approved {
    background: rgba(72, 187, 120, 0.15);
    border: 1px solid rgba(72, 187, 120, 0.4);
    color: #48bb78;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-block;
}

.badge-denied {
    background: rgba(245, 101, 101, 0.15);
    border: 1px solid rgba(245, 101, 101, 0.4);
    color: #fc8181;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-block;
}

.badge-counter {
    background: rgba(159, 122, 234, 0.15);
    border: 1px solid rgba(159, 122, 234, 0.4);
    color: #b794f4;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-block;
}

/* Agent pipeline cards */
.pipeline-card {
    background: rgba(26, 32, 44, 0.8);
    border: 1px solid rgba(99, 179, 237, 0.15);
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 0.75rem;
    transition: all 0.3s ease;
}

.pipeline-card.active {
    border-color: rgba(99, 179, 237, 0.5);
    background: rgba(15, 52, 96, 0.3);
    box-shadow: 0 0 20px rgba(99, 179, 237, 0.1);
}

.pipeline-card.done {
    border-color: rgba(72, 187, 120, 0.4);
    background: rgba(20, 40, 30, 0.4);
}

/* Agent message feed */
.agent-message {
    background: rgba(26, 32, 44, 0.9);
    border-left: 3px solid #63b3ed;
    border-radius: 0 8px 8px 0;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
    color: #e2e8f0;
}

.agent-message.intake { border-left-color: #63b3ed; }
.agent-message.risk   { border-left-color: #f6ad55; }
.agent-message.decision { border-left-color: #9f7aea; }
.agent-message.system { border-left-color: #68d391; }
.agent-message.thought { border-left-color: #718096; font-style: italic; opacity: 0.85; }
.agent-message.error { border-left-color: #fc8181; background: rgba(252, 129, 129, 0.05); }

/* Decision card */
.decision-card {
    background: linear-gradient(135deg, rgba(15, 52, 96, 0.6), rgba(26, 26, 46, 0.8));
    border: 1px solid rgba(99, 179, 237, 0.3);
    border-radius: 16px;
    padding: 2rem;
    margin-top: 1.5rem;
}

.decision-amount {
    font-size: 2.5rem;
    font-weight: 700;
    color: #48bb78;
}

/* Form styling */
.stSelectbox label, .stNumberInput label, .stTextInput label, .stSlider label {
    color: #a0aec0 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}

/* Section headers */
.section-header {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #63b3ed;
    margin-bottom: 1rem;
    margin-top: 0.5rem;
}

/* Human gate */
.human-gate {
    background: linear-gradient(135deg, rgba(49, 130, 206, 0.1), rgba(66, 153, 225, 0.05));
    border: 2px solid rgba(99, 179, 237, 0.4);
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
}

.stButton > button {
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.9rem;
    padding: 0.6rem 2rem;
}

div[data-testid="stMetricValue"] {
    color: #90cdf4 !important;
    font-size: 1.4rem !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────

if "pipeline_status" not in st.session_state:
    st.session_state.pipeline_status = "idle"
if "agent_messages" not in st.session_state:
    st.session_state.agent_messages = []
if "loan_decision" not in st.session_state:
    st.session_state.loan_decision = None
if "loan_letter" not in st.session_state:
    st.session_state.loan_letter = None
if "application_id" not in st.session_state:
    st.session_state.application_id = None
if "chat_id" not in st.session_state:
    st.session_state.chat_id = os.getenv("BAND_CHAT_ID", "")
if "intake_handle" not in st.session_state:
    _user = os.getenv("BAND_USER_HANDLE", "").strip().lstrip("@")
    st.session_state.intake_handle = os.getenv(
        "BAND_HANDLE_INTAKE", f"@{_user}/intakeagent" if _user else ""
    )
if "poll_since" not in st.session_state:
    st.session_state.poll_since = None
if "seen_message_ids" not in st.session_state:
    st.session_state.seen_message_ids = set()
if "active_demo" not in st.session_state:
    st.session_state.active_demo = None

# ─────────────────────────────────────────────
# DEMO SCENARIOS
# ─────────────────────────────────────────────

DEMO_SCENARIOS = {
    "good": {
        "label": "✅ Good Applicant",
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
    },
    "borderline": {
        "label": "⚠️ Borderline Applicant",
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
        "collateral_offered": None,
    },
    "highrisk": {
        "label": "❌ High Risk Applicant",
        "applicant_name": "Ravi Kumar",
        "applicant_age": 45,
        "monthly_income": 30000.0,
        "currency": "INR",
        "employment_type": "unemployed",
        "employer_name": None,
        "years_employed": 0.0,
        "loan_amount_requested": 500000.0,
        "loan_purpose": "personal",
        "loan_tenure_months": 36,
        "existing_debt_monthly": 18000.0,
        "credit_score": None,
        "collateral_offered": None,
    },
}

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def format_currency(amount, currency="INR"):
    if currency == "INR":
        return f"₹{amount:,.0f}"
    return f"${amount:,.0f}"


def detect_message_stage(text):
    if "NEW_LOAN_APPLICATION:" in text:   return "system"   # the UI's own kickoff message
    elif "LOAN_APPLICATION:" in text:     return "doc"
    elif "DOC_VERIFICATION:" in text:     return "credit"
    elif "CREDIT_ANALYSIS:" in text:      return "fraud"
    elif "FRAUD_REPORT:" in text:         return "risk"
    elif "RISK_ASSESSMENT:" in text:      return "compliance"
    elif "COMPLIANCE_CHECK:" in text:     return "decision"
    elif "LOAN_DECISION_READY:" in text:  return "pricing"
    elif "PRICING_TERMS:" in text:        return "communication"
    elif "FORMAL_LETTER_READY:" in text:  return "human_gate"
    elif "INTAKE_ERROR:" in text:         return "error"
    return "system"


def build_application_message(form_data):
    """Build the message to post to the Band room to kick off the pipeline."""
    return f"""NEW_LOAN_APPLICATION:
Applicant: {form_data['applicant_name']}, Age: {form_data['applicant_age']}
Monthly Income: {form_data['monthly_income']} {form_data['currency']}
Employment: {form_data['employment_type']} at {form_data.get('employer_name', 'N/A')} ({form_data['years_employed']} years)
Loan Request: {form_data['loan_amount_requested']} {form_data['currency']} for {form_data['loan_tenure_months']} months
Purpose: {form_data['loan_purpose']}
Existing Monthly Debt: {form_data['existing_debt_monthly']} {form_data['currency']}
Credit Score: {form_data.get('credit_score', 'Not provided')}
Collateral: {form_data.get('collateral_offered', 'None')}

Please process this application through the pipeline."""


def ingest_agent_message(msg_or_content: str | dict[str, Any]) -> bool:
    """Classify one Band message and update pipeline state.

    Returns True if the message advanced the pipeline (an agent output), False
    for the UI's own kickoff / unrecognized chatter. Shared by the auto-poller
    and the manual fallback so both behave identically.
    """
    if isinstance(msg_or_content, str):
        content = msg_or_content.strip()
        msg_type = "text"
        sender_name = "Agent"
        sender_type = "Agent"
    else:
        content = msg_or_content.get("content", "").strip()
        msg_type = msg_or_content.get("message_type", "text")
        sender = msg_or_content.get("sender") or {}
        sender_name = msg_or_content.get("sender_name")
        if not sender_name and isinstance(sender, dict):
            sender_name = sender.get("name")
        if not sender_name:
            sender_name = "System"

        sender_type = msg_or_content.get("sender_type")
        if not sender_type and isinstance(sender, dict):
            sender_type = sender.get("type")
        if not sender_type:
            sender_type = "User"

    stage = detect_message_stage(content)
    
    if msg_type == "thought":
        stage = "thought"
    elif msg_type == "error":
        stage = "error"

    # Skip UI kickoff and user chatter in the agent feed
    if stage == "system" and sender_type == "User":
        return False

    data = extract_json_from_message(content)

    # Decision Agent posts LOAN_DECISION_READY (stage 'pricing') with the recommendation.
    if stage == "pricing" and data:
        st.session_state.loan_decision = data
    # Pricing Agent posts PRICING_TERMS (stage 'communication') — merge final terms in.
    if stage == "communication" and data and st.session_state.loan_decision:
        st.session_state.loan_decision = {**st.session_state.loan_decision, **data}
    # Communication Agent posts FORMAL_LETTER_READY -> open the Human Gate.
    if stage == "human_gate" and data:
        st.session_state.loan_letter = data
        st.session_state.pipeline_status = "awaiting_approval"

    st.session_state.agent_messages.append({
        "stage": stage,
        "sender_name": sender_name,
        "time": datetime.now().strftime("%H:%M:%S"),
        "text": content,
    })
    return True


@st.fragment(run_every=2)
def auto_poll_band() -> None:
    """Every 2s while the pipeline is running, pull new agent messages and auto-advance."""
    if st.session_state.pipeline_status != "running":
        return

    if st.session_state.get("demo_safe_mode", True):
        scenario = st.session_state.get("replay_scenario", "good")
        step = st.session_state.get("replay_step", 0)
        from demo_replay import DEMO_REPLAY_DATA
        canned_msgs = DEMO_REPLAY_DATA.get(scenario, [])
        if step < len(canned_msgs):
            import sys
            # Skip sleep when running in automated tests to avoid timeouts
            is_testing = "streamlit.testing" in sys.modules or os.getenv("STREAMLIT_TESTING") == "true"
            if not is_testing:
                time.sleep(1.2)  # Simulate agent thinking/processing delay
            msg = canned_msgs[step]
            ingest_agent_message(msg)
            st.session_state.replay_step = step + 1
            st.rerun()
        return

    if not st.session_state.chat_id or not is_configured():
        return
    try:
        messages = poll_messages(st.session_state.chat_id, st.session_state.poll_since)
    except BandClientError:
        return  # transient — retry on the next tick

    # Process oldest-first so the feed order and the `since` cursor stay consistent.
    messages = sorted(messages, key=lambda m: m.get("inserted_at") or "")

    advanced = False
    for msg in messages:
        timestamp = msg.get("inserted_at")
        if timestamp:
            st.session_state.poll_since = timestamp
        msg_id = msg.get("id")
        if msg_id is not None:
            if msg_id in st.session_state.seen_message_ids:
                continue  # already ingested — avoid duplicate feed entries
            st.session_state.seen_message_ids.add(msg_id)
            
        sender = msg.get("sender") or {}
        sender_type = sender.get("type") if isinstance(sender, dict) else msg.get("sender_type")
        if sender_type == "User":
            continue  # skip the UI's own kickoff message
        if ingest_agent_message(msg):
            advanced = True

    if advanced:
        st.rerun()


# ─────────────────────────────────────────────
# ── AUDIT TRAIL & HUMAN GATE HELPERS ──
# ─────────────────────────────────────────────

import json
from typing import Any

def build_audit_json(messages: list[dict], decision: dict | None, application_id: str | None) -> str:
    """Format messages and final decision status into a readable JSON string."""
    audit_data = {
        "application_id": application_id,
        "exported_at": datetime.now().isoformat(),
        "final_decision": decision,
        "audit_trail": messages
    }
    return json.dumps(audit_data, indent=2)


def build_audit_pdf(messages: list[dict], decision: dict | None, application_id: str | None) -> bytes:
    """Generate a formatted PDF document containing the chronological audit trail."""
    from io import BytesIO
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    except ImportError:
        raise ImportError("reportlab package is required to export PDF.")

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1a365d'),
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=colors.HexColor('#4a5568'),
        spaceAfter=15
    )
    
    h2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#2b6cb0'),
        spaceBefore=12,
        spaceAfter=8
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#2d3748')
    )
    
    meta_style = ParagraphStyle(
        'MetaText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        textColor=colors.HexColor('#718096')
    )

    bold_body_style = ParagraphStyle(
        'BoldBodyText',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    
    story = []
    
    # Header
    story.append(Paragraph("LOAN SHARK FINANCIAL SERVICES", title_style))
    story.append(Paragraph(f"Compliance Audit Trail Record — Application ID: {application_id or 'N/A'}", subtitle_style))
    story.append(Spacer(1, 8))
    
    # Final Decision Callout if present
    if decision:
        story.append(Paragraph("Decision Summary", h2_style))
        rec = decision.get("recommendation", "N/A")
        risk = decision.get("risk_category", "N/A")
        conf = decision.get("confidence", "N/A")
        
        dec_data = [
            [Paragraph("Recommendation:", bold_body_style), Paragraph(str(rec), body_style)],
            [Paragraph("Risk Category:", bold_body_style), Paragraph(str(risk), body_style)],
            [Paragraph("Confidence Level:", bold_body_style), Paragraph(str(conf), body_style)],
        ]
        
        if decision.get("approved_amount"):
            dec_data.append([Paragraph("Approved Amount:", bold_body_style), Paragraph(f"Rs. {decision.get('approved_amount'):,}", body_style)])
        if decision.get("approved_tenure_months"):
            dec_data.append([Paragraph("Approved Tenure:", bold_body_style), Paragraph(f"{decision.get('approved_tenure_months')} months", body_style)])
        if decision.get("exact_interest_rate") or decision.get("interest_rate"):
            rate = decision.get("exact_interest_rate") or decision.get("interest_rate")
            dec_data.append([Paragraph("Interest Rate:", bold_body_style), Paragraph(str(rate), body_style)])
            
        t_dec = Table(dec_data, colWidths=[140, 360])
        t_dec.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f7fafc')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#edf2f7')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(t_dec)
        story.append(Spacer(1, 10))
        
        notes = decision.get("compliance_notes")
        if notes:
            story.append(Paragraph("Compliance Notes:", bold_body_style))
            story.append(Paragraph(str(notes), body_style))
            story.append(Spacer(1, 8))
            
    # Audit Trail Chronology
    story.append(Paragraph("Chronological Agent Processing Logs", h2_style))
    
    for idx, msg in enumerate(messages):
        stage = msg.get("stage", "system")
        sender = msg.get("sender_name", "Agent")
        timestamp = msg.get("time", "")
        text = msg.get("text", "")
        
        stage_label = {
            "doc": "Intake -> Document Handoff",
            "credit": "Document -> Credit Verification",
            "fraud": "Credit -> Credit Analysis",
            "risk": "Credit -> Fraud Assessment",
            "compliance": "Fraud -> Risk Assessment",
            "decision": "Risk -> Compliance Check",
            "pricing": "Compliance -> Loan Decision",
            "communication": "Decision -> Pricing Terms",
            "human_gate": "Pricing -> Sanction Letter Draft",
            "system": "System Log",
            "thought": "Agent Internal Thought",
            "error": "Pipeline Error",
        }.get(stage, stage.capitalize())
        
        header_text = f"Step {idx+1}: {stage_label} ({sender}) — {timestamp}"
        story.append(Paragraph(header_text, bold_body_style))
        
        json_data = extract_json_from_message(text)
        if json_data:
            fields_data = []
            for k, v in json_data.items():
                if k not in ["letter_body", "compliance_notes"] and v is not None:
                    fields_data.append([Paragraph(str(k), meta_style), Paragraph(str(v), meta_style)])
            if fields_data:
                t_fields = Table(fields_data, colWidths=[140, 360])
                t_fields.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#edf2f7')),
                    ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
                    ('INNERGRID', (0,0), (-1,-1), 0.25, colors.HexColor('#edf2f7')),
                    ('TOPPADDING', (0,0), (-1,-1), 2),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                    ('LEFTPADDING', (0,0), (-1,-1), 8),
                ]))
                story.append(t_fields)
            else:
                story.append(Paragraph("JSON payload carries forward cumulative variables.", meta_style))
        else:
            story.append(Paragraph(text, body_style))
            
        story.append(Spacer(1, 5))
        
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def render_audit_panel(messages: list[dict], decision: dict | None, application_id: str | None) -> None:
    """Renders the compliance audit trail expander and exports in the UI."""
    if not messages:
        return

    st.markdown('<div class="section-header">📋 Compliance Audit Trail</div>', unsafe_allow_html=True)
    with st.expander("📄 Open Regulatory Compliance & Audit Log", expanded=False):
        
        # Prominent Decision Basis Callout
        if decision:
            st.markdown("### ⚖️ Decision Basis Summary")
            rec = decision.get("recommendation", "N/A")
            risk = decision.get("risk_category", "N/A")
            compliance_verdict = decision.get("compliance_verdict", "N/A")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Recommendation", rec)
            with c2:
                st.metric("Risk Category", risk)
            with c3:
                st.metric("Compliance Verdict", compliance_verdict)
                
            # Call out compliance notes / violations prominently
            notes = decision.get("compliance_notes")
            if notes:
                st.info(f"**Regulatory Note:** {notes}")
                
            denial = decision.get("denial_reasons")
            if rec == "DENY" and denial:
                st.error("**Denial Reasons & Violations:**\n" + "\n".join(f"• {r}" for r in denial))
            
            st.divider()

        # Chronological Audit List
        st.markdown("### 📜 Chronological Processing Log")
        for idx, msg in enumerate(messages):
            sender = msg.get("sender_name", "Agent")
            stage = msg.get("stage", "system")
            timestamp = msg.get("time", "")
            text = msg.get("text", "")
            
            stage_title = {
                "doc":           f"📥 {sender} → Document Handoff",
                "credit":        f"📄 {sender} → Credit Verification",
                "fraud":         f"💳 {sender} → Credit Analysis",
                "risk":          f"🔍 {sender} → Fraud Assessment",
                "compliance":    f"📊 {sender} → Risk Assessment",
                "decision":      f"⚖️ {sender} → Compliance Check",
                "pricing":       f"🎯 {sender} → Loan Decision",
                "communication": f"💰 {sender} → Pricing Terms",
                "human_gate":    f"✉️ {sender} → Sanction Letter",
                "system":        "⚙️ System Action Log",
                "thought":       f"🧠 {sender} (Thinking)",
                "error":         f"⚠️ {sender} (Error)",
            }.get(stage, f"{sender} (Action)")

            st.markdown(f"**Step {idx+1}: {stage_title}** · *{timestamp}*")
            
            json_data = extract_json_from_message(text)
            if json_data:
                # Show key fields table
                display_data = {k: v for k, v in json_data.items() if k not in ["letter_body", "compliance_notes"] and v is not None}
                st.json(display_data, expanded=False)
            else:
                st.text(text)
            st.markdown("---")
            
        # Download buttons
        col_json, col_pdf = st.columns(2)
        
        # JSON export
        json_data = build_audit_json(messages, decision, application_id)
        with col_json:
            st.download_button(
                label="📥 Download JSON Record",
                data=json_data,
                file_name=f"audit_{application_id or 'loan'}.json",
                mime="application/json",
                use_container_width=True
            )
            
        # PDF export
        with col_pdf:
            try:
                pdf_data = build_audit_pdf(messages, decision, application_id)
                st.download_button(
                    label="📥 Download PDF Record",
                    data=pdf_data,
                    file_name=f"audit_{application_id or 'loan'}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.button(
                    "📥 Download PDF (Install reportlab)",
                    disabled=True,
                    help=f"PDF export requires reportlab. Error: {e}",
                    use_container_width=True
                )


def render_human_gate() -> None:
    """Reads st.session_state.loan_letter / loan_decision; renders gate; logs officer action."""
    letter = st.session_state.loan_letter
    decision = st.session_state.loan_decision or {}
    rec = letter.get("recommendation", decision.get("recommendation", ""))
    
    st.divider()
    st.markdown('<div class="section-header">🔐 Human Loan Officer Review</div>', unsafe_allow_html=True)

    # Decision summary
    badge_map = {
        "APPROVE": ("badge-approved", "✅ APPROVE"),
        "DENY": ("badge-denied", "❌ DENY"),
        "COUNTER_OFFER": ("badge-counter", "🔄 COUNTER OFFER"),
    }
    badge_cls, badge_text = badge_map.get(rec, ("badge-processing", rec))

    st.markdown(f"""
    <div class="decision-card">
        <div style="margin-bottom:1rem">
            <span class="{badge_cls}">{badge_text}</span>
            <span style="color:#718096; font-size:0.8rem; margin-left:1rem">
                Application {decision.get('application_id', '')} · 
                Risk: {decision.get('risk_category', '')} · 
                Confidence: {decision.get('confidence', '')}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Allow adjustments on Counter Offer
    is_counter_offer = (rec == "COUNTER_OFFER")
    final_amount = decision.get("approved_amount") or letter.get("approved_amount", 0.0)
    final_tenure = decision.get("approved_tenure_months") or letter.get("approved_tenure_months", 0)

    if rec in ("APPROVE", "COUNTER_OFFER") and decision:
        if is_counter_offer:
            st.markdown("#### 🛠️ Adjust Counter-Offer Terms")
            col_adj_1, col_adj_2 = st.columns(2)
            with col_adj_1:
                final_amount = st.number_input(
                    "Approved Amount (INR)",
                    min_value=10000.0,
                    max_value=float(decision.get("loan_amount_requested") or 10000000.0),
                    value=float(final_amount),
                    step=10000.0,
                    key="adj_amount"
                )
            with col_adj_2:
                final_tenure = st.number_input(
                    "Approved Tenure (months)",
                    min_value=6,
                    max_value=360,
                    value=int(final_tenure),
                    step=6,
                    key="adj_tenure"
                )
            # Recalculate EMI roughly for display
            rate_str = decision.get("exact_interest_rate") or "12%"
            try:
                rate_val = float(rate_str.replace("%", "").split()[0]) / 100.0
            except Exception:
                rate_val = 0.12
            monthly_rate = rate_val / 12.0
            n = final_tenure
            if monthly_rate > 0 and n > 0:
                final_emi = final_amount * (monthly_rate * (1 + monthly_rate)**n) / ((1 + monthly_rate)**n - 1)
            else:
                final_emi = 0.0
        else:
            final_emi = decision.get("final_emi") or decision.get("estimated_emi", 0.0)

        # Show metrics
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Loan Amount", format_currency(final_amount))
        with m2:
            st.metric("Tenure", f"{final_tenure} months")
        with m3:
            st.metric("Estimated EMI", format_currency(final_emi) + "/mo")

        co_notes = decision.get("counter_offer_notes") or letter.get("counter_offer_notes")
        if co_notes and not is_counter_offer:
            st.info(f"**Counter Offer Notes:** {co_notes}")

    denial = decision.get("denial_reasons") or letter.get("denial_reasons", [])
    if rec == "DENY" and denial:
        st.error("**Denial Reasons:**\n" + "\n".join(f"• {r}" for r in denial))

    # Formal Letter Preview
    if letter.get("letter_body"):
        st.divider()
        st.markdown('<div class="section-header">📝 Formal Letter Preview</div>', unsafe_allow_html=True)
        letter_body = letter['letter_body']
        if is_counter_offer:
            letter_body = letter_body.replace(f"Rs {decision.get('approved_amount', 0):,}", f"Rs {final_amount:,}")
            letter_body = letter_body.replace(f"{decision.get('approved_tenure_months', 0)} Months", f"{final_tenure} Months")
            
        letter_html = letter_body.replace('\\n', '<br>').replace('\n', '<br>')
        st.markdown(f"""
        <div style="
            background: rgba(20,30,48,0.8);
            border: 1px solid rgba(99,179,237,0.2);
            border-radius: 12px;
            padding: 1.5rem 2rem;
            font-family: 'Georgia', serif;
            font-size: 0.82rem;
            line-height: 1.8;
            color: #e2e8f0;
            max-height: 250px;
            overflow-y: auto;
        ">
            {letter_html}
        </div>
        """, unsafe_allow_html=True)

    # Compliance Notes Summary
    audit = decision.get("compliance_notes", "")
    if audit:
        with st.expander("📄 Compliance Notes Summary"):
            st.text(audit)

    st.divider()
    st.markdown("#### 👤 Loan Officer Sign-off")
    
    # Name input
    officer_name = st.text_input("Officer Name", value=st.session_state.get("officer_name", ""), placeholder="e.g. Navnit Nair", key="officer_name_input")
    st.session_state.officer_name = officer_name

    # Compliance Checklist
    st.markdown("**Compliance Checklist:**")
    chk1 = st.checkbox("KYC verified and applicant identity confirmed", key="chk_kyc")
    chk2 = st.checkbox("Interest rate and EMI affordability reviewed", key="chk_afford")
    chk3 = st.checkbox("Lending terms compliant with RBI regulatory guidelines", key="chk_rbi")
    
    all_checked = chk1 and chk2 and chk3
    officer_filled = bool(officer_name.strip())

    col_a, col_b = st.columns(2)
    
    show_override = st.session_state.get("show_override_reason_input", False)
    
    if not show_override:
        with col_a:
            st.button(
                "✅ Approve & Finalize",
                type="primary",
                use_container_width=True,
                disabled=not (all_checked and officer_filled),
                key="btn_approve_finalize"
            )
            if st.session_state.get("btn_approve_finalize"):
                st.session_state.pipeline_status = "complete"
                time_str = datetime.now().strftime("%H:%M:%S")
                st.session_state.agent_messages.append({
                    "stage": "system",
                    "time": time_str,
                    "sender_name": "System",
                    "text": f"✅ APPROVED by {officer_name} at {time_str} — amount {format_currency(final_amount)}, tenure {final_tenure} mo. Final terms logged.",
                })
                st.rerun()
        with col_b:
            st.button(
                "❌ Reject / Override",
                use_container_width=True,
                disabled=not officer_filled,
                key="btn_reject_override"
            )
            if st.session_state.get("btn_reject_override"):
                st.session_state.show_override_reason_input = True
                st.rerun()
    else:
        st.warning("⚠️ Enter a reason for overriding/rejecting the recommendation:")
        reason = st.text_area("Override/Rejection Reason", key="override_reason_text_input")
        
        col_c, col_d = st.columns(2)
        with col_c:
            st.button(
                "Confirm Override / Rejection",
                type="primary",
                use_container_width=True,
                disabled=(reason.strip() == ""),
                key="btn_confirm_override"
            )
            if st.session_state.get("btn_confirm_override"):
                st.session_state.pipeline_status = "complete"
                st.session_state.show_override_reason_input = False
                time_str = datetime.now().strftime("%H:%M:%S")
                st.session_state.agent_messages.append({
                    "stage": "system",
                    "time": time_str,
                    "sender_name": "System",
                    "text": f"🚫 OVERRIDDEN by {officer_name} at {time_str} — reason: \"{reason}\". Decision logged.",
                })
                st.rerun()
        with col_d:
            if st.button("Cancel Override", use_container_width=True):
                st.session_state.show_override_reason_input = False
                st.rerun()



# ─────────────────────────────────────────────
# LAYOUT
# ─────────────────────────────────────────────

# Header
st.markdown("""
<div class="lp-header">
    <div>
        <p class="lp-title">🦈 Loan Shark</p>
        <p class="lp-subtitle">AI-Powered Loan Processing · 9-Agent Pipeline · Regulated & Audited</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Two-column layout
left_col, right_col = st.columns([1.1, 0.9], gap="large")

# ─────────────────────────────────────────────
# LEFT: APPLICATION FORM
# ─────────────────────────────────────────────

with left_col:
    # ── QUICK DEMO BUTTONS ──
    st.markdown('<div class="section-header">⚡ Quick Demo</div>', unsafe_allow_html=True)
    d1, d2, d3 = st.columns(3)
    with d1:
        if st.button("✅ Good Applicant", use_container_width=True, help="Salaried, 768 credit score → likely APPROVE"):
            st.session_state.active_demo = "good"
            st.rerun()
    with d2:
        if st.button("⚠️ Borderline", use_container_width=True, help="Self-employed, 648 score → likely COUNTER_OFFER"):
            st.session_state.active_demo = "borderline"
            st.rerun()
    with d3:
        if st.button("❌ High Risk", use_container_width=True, help="Unemployed, no credit score → likely DENY"):
            st.session_state.active_demo = "highrisk"
            st.rerun()

    if st.session_state.active_demo:
        demo = DEMO_SCENARIOS[st.session_state.active_demo]
        st.info(f"📋 Demo loaded: **{demo['label']}** — fill in Band credentials below and click Submit.")

    st.divider()
    st.markdown('<div class="section-header">📋 Loan Application</div>', unsafe_allow_html=True)

    # Get demo defaults if a scenario is active
    _d = DEMO_SCENARIOS.get(st.session_state.active_demo or "", {})

    with st.form("loan_form", clear_on_submit=False):

        # Personal Info
        st.markdown("**Personal Information**")
        col1, col2 = st.columns(2)
        with col1:
            applicant_name = st.text_input("Full Name", value=_d.get("applicant_name", ""), placeholder="Rahul Sharma")
            applicant_age = st.number_input("Age", min_value=18, max_value=70, value=int(_d.get("applicant_age", 30)))
        with col2:
            credit_score = st.number_input(
                "Credit Score (leave 0 if unknown)",
                min_value=0, max_value=900, value=int(_d.get("credit_score") or 0),
                help="CIBIL/credit score, 300–900 range"
            )
            currency = st.selectbox("Currency", ["INR", "USD"])

        st.divider()

        # Employment
        st.markdown("**Employment Details**")
        col3, col4 = st.columns(2)
        with col3:
            emp_opts = ["salaried", "self_employed", "business_owner", "unemployed"]
            emp_default = emp_opts.index(_d["employment_type"]) if _d.get("employment_type") in emp_opts else 0
            employment_type = st.selectbox("Employment Type", emp_opts, index=emp_default)
            employer_name = st.text_input("Employer / Business Name", value=_d.get("employer_name") or "", placeholder="TCS, Infosys, Self...")
        with col4:
            monthly_income = st.number_input(
                "Monthly Income", min_value=0.0, value=float(_d.get("monthly_income", 75000.0)), step=5000.0
            )
            years_employed = st.number_input(
                "Years at Current Job", min_value=0.0, max_value=40.0, value=float(_d.get("years_employed", 3.0)), step=0.5
            )

        st.divider()

        # Loan Details
        st.markdown("**Loan Request**")
        col5, col6 = st.columns(2)
        with col5:
            loan_amount = st.number_input(
                "Loan Amount", min_value=10000.0, value=float(_d.get("loan_amount_requested", 500000.0)), step=10000.0
            )
            loan_opts = ["home", "vehicle", "education", "personal", "business"]
            loan_purpose_default = loan_opts.index(_d["loan_purpose"]) if _d.get("loan_purpose") in loan_opts else 0
            loan_purpose = st.selectbox("Loan Purpose", loan_opts, index=loan_purpose_default)
        with col6:
            loan_tenure = st.slider(
                "Tenure (months)", min_value=6, max_value=360, value=int(_d.get("loan_tenure_months", 60)), step=6
            )
            existing_debt = st.number_input(
                "Existing Monthly Debt Payments",
                min_value=0.0, value=0.0, step=1000.0,
                help="Total EMIs you already pay every month"
            )

        collateral = st.text_input(
            "Collateral Offered (optional)",
            placeholder="Property at Delhi, Vehicle registration...",
        )

        st.divider()

        # Band Connection
        st.markdown("**Band Connection**")
        band_chat_id = st.text_input(
            "Band Chat / Room ID",
            value=st.session_state.chat_id,
            placeholder="chat_id of your LoanShark room",
            help="From app.band.ai — the room where all 9 agents are participants",
        )
        intake_handle = st.text_input(
            "Intake Agent Handle (@mention to start)",
            value=st.session_state.intake_handle,
            placeholder="@yourusername/IntakeAgent",
            help="Band routes the kickoff to this handle — must match the Intake agent's handle.",
        )
        band_human_key = st.text_input(
            "Band Human API Key",
            type="password",
            placeholder="Leave blank if set in .env (BAND_HUMAN_API_KEY)",
            help="Your personal Band API key — the UI uses it to post and poll messages.",
        )
        demo_safe_mode = st.checkbox(
            "🛡️ Demo-safe Mode (Simulated Replay)",
            value=st.session_state.get("demo_safe_mode", True),
            help="Bypass live Band SDK/API calls and run a realistic, canned sequence of agent steps on a timer. Safe for offline or quota issues."
        )

        submitted = st.form_submit_button(
            "🚀 Submit Application",
            use_container_width=True,
            type="primary"
        )

    if submitted:
        st.session_state.demo_safe_mode = demo_safe_mode
        if band_human_key.strip():
            os.environ["BAND_HUMAN_API_KEY"] = band_human_key.strip()
        if band_chat_id.strip():
            os.environ["BAND_CHAT_ID"] = band_chat_id.strip()

        if not demo_safe_mode and (not applicant_name or not band_chat_id.strip() or not intake_handle.strip()):
            st.error("Please fill in applicant name, Band Chat ID, and Intake Agent Handle.")
        elif not demo_safe_mode and not is_configured():
            st.error(
                f"Band not configured — missing: {', '.join(missing_config())}. "
                "Set BAND_HUMAN_API_KEY in .env or paste it in the field above."
            )
        else:
            form_data = {
                "applicant_name": applicant_name,
                "applicant_age": applicant_age,
                "monthly_income": monthly_income,
                "currency": currency,
                "employment_type": employment_type,
                "employer_name": employer_name if employer_name else None,
                "years_employed": years_employed,
                "loan_amount_requested": loan_amount,
                "loan_purpose": loan_purpose,
                "loan_tenure_months": loan_tenure,
                "existing_debt_monthly": existing_debt,
                "credit_score": credit_score if credit_score > 0 else None,
                "collateral_offered": collateral if collateral else None,
            }

            message = build_application_message(form_data)
            app_id = f"APP-{str(int(time.time()))[-6:]}"
            chat_id = band_chat_id.strip()
            handle = intake_handle.strip()
            st.session_state.application_id = app_id
            st.session_state.chat_id = chat_id
            st.session_state.intake_handle = handle
            st.session_state.pipeline_status = "running"
            st.session_state.agent_messages = []
            st.session_state.loan_decision = None
            st.session_state.loan_letter = None
            st.session_state.seen_message_ids = set()
            st.session_state.show_override_reason_input = False

            if demo_safe_mode:
                st.session_state.replay_step = 0
                st.session_state.replay_scenario = st.session_state.active_demo or "good"
                st.session_state.agent_messages.append({
                    "stage": "system",
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "text": f"✅ Simulated Application {app_id} submitted. Running in Demo-safe Mode...",
                })
            else:
                st.session_state.poll_since = now_iso()
                st.session_state.agent_messages.append({
                    "stage": "system",
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "text": f"✅ Application {app_id} submitted. Triggering 9-agent pipeline via Band...",
                })

                # Post the kickoff to the Band room via the Human API (must @mention Intake).
                content = f"{handle} {message}"
                try:
                    post_message(chat_id, content, mention_handle=handle)
                    st.session_state.agent_messages.append({
                        "stage": "system",
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "text": "📡 Posted to Band. Agents are processing — the pipeline will advance automatically...",
                    })
                    st.success("Submitted to Band! Watch the pipeline auto-advance on the right →")
                except BandClientError as exc:
                    st.session_state.pipeline_status = "idle"
                    st.session_state.agent_messages.append({
                        "stage": "error",
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "text": f"⚠️ Could not post to Band: {exc}",
                    })
                    st.error(f"Could not post to Band room: {exc}")

            st.rerun()


# ─────────────────────────────────────────────
# RIGHT: PIPELINE STATUS + AGENT FEED
# ─────────────────────────────────────────────

with right_col:

    # Pipeline status
    st.markdown('<div class="section-header">🤖 Agent Pipeline</div>', unsafe_allow_html=True)

    status = st.session_state.pipeline_status
    intake_done     = any(m["stage"] == "doc"          for m in st.session_state.agent_messages)
    doc_done        = any(m["stage"] == "credit"        for m in st.session_state.agent_messages)
    credit_done     = any(m["stage"] == "fraud"         for m in st.session_state.agent_messages)
    fraud_done      = any(m["stage"] == "risk"          for m in st.session_state.agent_messages)
    risk_done       = any(m["stage"] == "compliance"    for m in st.session_state.agent_messages)
    compliance_done = any(m["stage"] == "decision"      for m in st.session_state.agent_messages)
    decision_done   = any(m["stage"] == "pricing"       for m in st.session_state.agent_messages)
    pricing_done    = any(m["stage"] == "communication" for m in st.session_state.agent_messages)
    comm_done       = (st.session_state.loan_letter is not None
                       or any(m["stage"] == "human_gate" for m in st.session_state.agent_messages))

    all_stages = [
        ("Intake Agent",        "📥", intake_done),
        ("Document Agent",      "📄", doc_done),
        ("Credit Agent",        "💳", credit_done),
        ("Fraud Agent",         "🔍", fraud_done),
        ("Risk Agent",          "📊", risk_done),
        ("Compliance Agent",    "⚖️", compliance_done),
        ("Decision Agent",      "🎯", decision_done),
        ("Pricing Agent",       "💰", pricing_done),
        ("Communication Agent", "✉️", comm_done),
    ]

    done_list = [intake_done, doc_done, credit_done, fraud_done,
                 risk_done, compliance_done, decision_done, pricing_done, comm_done]

    for step_num, (agent_name, icon, done) in enumerate(all_stages):
        prev_done = done_list[step_num - 1] if step_num > 0 else True
        active = status == "running" and prev_done and not done
        card_class = "done" if done else ("active" if active else "pipeline-card")
        indicator = "✅" if done else ("🔄" if active else "⏳")
        status_text = "Complete" if done else ("Processing..." if active else "Waiting")
        st.markdown(f"""
        <div class="pipeline-card {card_class}">
            <span style="font-size:1.1rem">{icon}</span>
            <strong style="color:#e2e8f0; margin-left:0.5rem; font-size:0.85rem">{agent_name}</strong>
            <span style="float:right; font-size:0.75rem; color:#a0aec0">{indicator} {status_text}</span>
        </div>
        """, unsafe_allow_html=True)

    # Auto-advance: poll Band every 2s while the pipeline is running
    auto_poll_band()

    st.divider()

    # Agent message feed
    st.markdown('<div class="section-header">💬 Live Agent Feed</div>', unsafe_allow_html=True)

    if not st.session_state.agent_messages:
        st.markdown(
            "<div style='color:#4a5568; text-align:center; padding:2rem; font-size:0.9rem'>"
            "Agent messages will appear here once you submit an application."
            "</div>",
            unsafe_allow_html=True
        )
    else:
        for msg in st.session_state.agent_messages:
            sender_name = msg.get("sender_name", "Agent")
            stage_label = {
                "doc":           f"📥 {sender_name} → Document Handoff",
                "credit":        f"📄 {sender_name} → Credit Verification",
                "fraud":         f"💳 {sender_name} → Credit Analysis",
                "risk":          f"🔍 {sender_name} → Fraud Assessment",
                "compliance":    f"📊 {sender_name} → Risk Assessment",
                "decision":      f"⚖️ {sender_name} → Compliance Check",
                "pricing":       f"🎯 {sender_name} → Loan Decision",
                "communication": f"💰 {sender_name} → Pricing Terms",
                "human_gate":    f"✉️ {sender_name} → Sanction Letter",
                "system":        "System",
                "thought":       f"🧠 {sender_name} (Thinking)",
                "error":         f"⚠️ {sender_name} (Error)",
            }.get(msg["stage"], sender_name)

            color = {
                "doc":           "#63b3ed",
                "credit":        "#76e4f7",
                "fraud":         "#fbd38d",
                "risk":          "#fc8181",
                "compliance":    "#b794f4",
                "decision":      "#f6ad55",
                "pricing":       "#68d391",
                "communication": "#9f7aea",
                "human_gate":    "#ed64a6",
                "system":        "#a0aec0",
                "thought":       "#718096",
                "error":         "#fc8181",
            }.get(msg["stage"], "#a0aec0")

            st.markdown(f"""
            <div class="agent-message {msg['stage']}">
                <span style="font-size:0.7rem; color:{color}; font-weight:700">
                    {stage_label} · {msg['time']}
                </span><br/>
                {msg['text'][:800]}{'...' if len(msg['text']) > 800 else ''}
            </div>
            """, unsafe_allow_html=True)

    # Manual fallback — only needed if the UI cannot reach Band to auto-poll
    if status == "running":
        with st.expander("📥 Manual fallback — paste an agent message"):
            st.caption("Auto-advance polls Band every 2s. Use this only if polling is unavailable.")
            agent_response = st.text_area("Paste Band room message here:", height=130, key="agent_paste")
            if st.button("Process Message", use_container_width=True):
                if agent_response:
                    ingest_agent_message(agent_response)
                    st.rerun()

    # ─── HUMAN GATE ───
    if status == "awaiting_approval" and st.session_state.loan_letter:
        render_human_gate()

    # Render Audit Trail Panel
    render_audit_panel(st.session_state.agent_messages, st.session_state.loan_decision, st.session_state.application_id)

    # ─── COMPLETE ───
    if status == "complete":
        st.success("🎉 Application finalized. Audit trail logged.")
        if st.button("Process New Application", use_container_width=True):
            st.session_state.pipeline_status = "idle"
            st.session_state.agent_messages = []
            st.session_state.loan_decision = None
            st.session_state.loan_letter = None
            st.session_state.application_id = None
            st.rerun()

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#4a5568; font-size:0.75rem'>"
    "Loan Shark · Built with Band SDK · Track 3: Regulated & High-Stakes Workflows · "
    "Team TrenCoders · Band of Agents Hackathon 2026"
    "</div>",
    unsafe_allow_html=True
)

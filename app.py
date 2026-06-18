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
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# GLOBAL CSS — matches FINEbank layout exactly
# ─────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── Main background: light gray ── */
.stApp, [data-testid="stAppViewContainer"] {
    background: #f0f2f5 !important;
}
[data-testid="stAppViewContainer"] > section:nth-child(2) {
    background: #f0f2f5 !important;
}
[data-testid="block-container"] {
    background: #f0f2f5 !important;
    padding: 2rem 2.5rem !important;
    max-width: 100% !important;
}

/* ── Sidebar: dark ── */
[data-testid="stSidebar"] {
    background: #1a1d27 !important;
    min-width: 240px !important;
    max-width: 240px !important;
    border-right: none !important;
}
[data-testid="stSidebar"] > div {
    padding-top: 0 !important;
}

/* Hide streamlit default sidebar header */
[data-testid="stSidebarNav"] { display: none !important; }
button[data-testid="collapsedControl"] { display: none !important; }

/* ── Sidebar Radio (nav pills) ── */
/* Hide the radio circles — target every Streamlit version */
div[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child { display: none !important; }
div[data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child { display: none !important; }
div[data-testid="stSidebar"] input[type="radio"] { display: none !important; }
div[data-testid="stSidebar"] [role="radio"] { display: none !important; }
div[data-testid="stSidebar"] .st-emotion-cache-1inwz65 { display: none !important; }
div[data-testid="stSidebar"] span[data-baseweb="radio"] > div:first-child { display: none !important; }
div[data-testid="stSidebar"] [role="radiogroup"] {
    gap: 0 !important;
}
div[data-testid="stSidebar"] [role="radiogroup"] label {
    background: transparent !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.7rem 1.2rem !important;
    margin: 0.15rem 0.8rem !important;
    cursor: pointer !important;
    transition: all 0.18s ease !important;
    width: calc(100% - 1.6rem) !important;
}
div[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(255,255,255,0.06) !important;
}
div[data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"] {
    background: #1dbfa0 !important;
    border-radius: 8px !important;
}
div[data-testid="stSidebar"] [role="radiogroup"] label p,
div[data-testid="stSidebar"] [role="radiogroup"] label span {
    color: #9ca3af !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
}
div[data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"] p,
div[data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"] span {
    color: #ffffff !important;
    font-weight: 600 !important;
}

/* ── White card ── */
.ls-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.ls-card-title {
    font-size: 1rem;
    font-weight: 600;
    color: #6b7280;
    margin: 0 0 1.4rem 0;
    letter-spacing: 0.01em;
}

/* ── Detail grid (2 or 3 col) ── */
.ls-detail-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.8rem;
    margin-bottom: 1.4rem;
}
.ls-detail-label {
    font-size: 0.78rem;
    color: #9ca3af;
    font-weight: 500;
    margin: 0 0 0.25rem 0;
    text-transform: capitalize;
}
.ls-detail-value {
    font-size: 1rem;
    font-weight: 700;
    color: #111827;
    margin: 0;
}

/* ── Action row ── */
.ls-action-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-top: 0.5rem;
}
.ls-btn-teal {
    background: #1dbfa0;
    color: #ffffff;
    padding: 0.55rem 1.4rem;
    border-radius: 7px;
    font-weight: 600;
    font-size: 0.88rem;
    cursor: pointer;
    display: inline-block;
    border: none;
    transition: background 0.15s;
}
.ls-btn-teal:hover { background: #18a88d; }
.ls-btn-ghost {
    color: #6b7280;
    font-size: 0.88rem;
    font-weight: 500;
    cursor: pointer;
    text-decoration: none;
    background: none;
    border: none;
}

/* ── Table ── */
.ls-table-wrap { overflow-x: auto; }
.ls-table {
    width: 100%;
    border-collapse: collapse;
}
.ls-table th {
    text-align: left;
    font-size: 0.83rem;
    font-weight: 700;
    color: #111827;
    padding: 0 1rem 1rem 0;
    border-bottom: 1px solid #e5e7eb;
}
.ls-table td {
    font-size: 0.88rem;
    color: #6b7280;
    padding: 1rem 1rem 1rem 0;
    border-bottom: 1px solid #f3f4f6;
    vertical-align: middle;
}
.ls-table td.bold { font-weight: 700; color: #111827; }
.ls-table td.green { color: #10b981; font-weight: 500; }
.ls-table td.red { color: #ef4444; font-weight: 500; }
.ls-table td.orange { color: #f59e0b; font-weight: 500; }
.ls-table td.blue { color: #3b82f6; font-weight: 500; }

/* Badge for pipeline stage */
.ls-badge {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}
.ls-badge-green { background: #d1fae5; color: #065f46; }
.ls-badge-orange { background: #fef3c7; color: #92400e; }
.ls-badge-red { background: #fee2e2; color: #991b1b; }
.ls-badge-blue { background: #dbeafe; color: #1e40af; }
.ls-badge-gray { background: #f3f4f6; color: #374151; }

/* ── Top bar ── */
.ls-topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.8rem;
}
.ls-topbar-date {
    font-size: 0.88rem;
    color: #9ca3af;
    font-weight: 500;
}
.ls-topbar-right {
    display: flex;
    align-items: center;
    gap: 1rem;
}
.ls-search {
    background: #ffffff;
    border: none;
    border-radius: 25px;
    padding: 0.5rem 1.2rem;
    font-size: 0.85rem;
    color: #9ca3af;
    width: 200px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    outline: none;
}

/* ── Load More button ── */
.ls-load-more-wrap { text-align: center; margin-top: 1.5rem; }
.ls-load-more {
    background: #1dbfa0;
    color: #fff;
    border: none;
    border-radius: 7px;
    padding: 0.6rem 2.5rem;
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
}

/* ── Streamlit form styling override ── */
div[data-testid="stForm"] {
    background: #ffffff;
    border-radius: 12px;
    padding: 1.8rem 2rem;
    border: none !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.stTextInput > label, .stNumberInput > label,
.stSelectbox > label, .stSlider > label,
.stTextArea > label, .stCheckbox > label {
    color: #374151 !important;
    font-size: 0.83rem !important;
    font-weight: 500 !important;
}
.stTextInput input, .stNumberInput input, .stTextArea textarea {
    background: #f9fafb !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 7px !important;
    color: #111827 !important;
    font-size: 0.9rem !important;
}
.stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
    border-color: #1dbfa0 !important;
    box-shadow: 0 0 0 2px rgba(29,191,160,0.15) !important;
}
.stSelectbox > div > div {
    background: #f9fafb !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 7px !important;
    color: #111827 !important;
}
.stFormSubmitButton > button, .stButton > button[kind="primary"] {
    background: #1dbfa0 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    padding: 0.65rem 2rem !important;
    transition: background 0.15s !important;
}
.stFormSubmitButton > button:hover { background: #18a88d !important; }
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    transition: all 0.15s !important;
}

/* ── Streamlit Slider ── */
.stSlider [data-baseweb="slider"] [data-testid="stThumbValue"] { color: #1dbfa0 !important; }
.stSlider [data-baseweb="slider"] [role="slider"] { background: #1dbfa0 !important; border-color: #1dbfa0 !important; }

/* ── Toggle ── */
div[data-testid="stSidebar"] .stToggle label { color: #9ca3af !important; font-size: 0.82rem !important; }

/* ── Hide default Streamlit elements ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stHeader"] { display: none; }
div[data-testid="stDecoration"] { display: none; }

/* ── Agent message feed ── */
.agent-message {
    background: #f9fafb;
    border-left: 3px solid #1dbfa0;
    border-radius: 0 8px 8px 0;
    padding: 0.7rem 1rem;
    margin-bottom: 0.5rem;
    font-size: 0.83rem;
    color: #374151;
}
.agent-message.error { border-left-color: #ef4444; background: #fef2f2; }
.agent-message.system { border-left-color: #6b7280; }
.agent-message.thought { border-left-color: #9ca3af; font-style: italic; opacity: 0.85; }

/* ── Decision / human gate ── */
.decision-card {
    background: #f0fdf4;
    border: 1px solid #86efac;
    border-radius: 10px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
}
.decision-card.deny { background: #fef2f2; border-color: #fca5a5; }
.decision-card.counter { background: #fffbeb; border-color: #fcd34d; }

/* ── Compliance expander ── */
.streamlit-expanderHeader { color: #374151 !important; font-size: 0.88rem !important; }

/* ── Section headers ── */
.ls-section-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #9ca3af;
    margin: 0 0 0.8rem 0;
}

/* ── Divider ── */
hr { border-color: #e5e7eb !important; margin: 1.2rem 0 !important; }

/* ── Metrics ── */
div[data-testid="stMetricValue"] { color: #111827 !important; font-size: 1.3rem !important; font-weight: 700 !important; }
div[data-testid="stMetricLabel"] { color: #6b7280 !important; font-size: 0.78rem !important; }

/* ── Info/Warning/Error boxes ── */
div[data-testid="stAlert"] { border-radius: 8px !important; font-size: 0.88rem !important; }

/* ── Expander ── */
div[data-testid="stExpander"] { border: 1px solid #e5e7eb !important; border-radius: 8px !important; }
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
if "current_page" not in st.session_state:
    st.session_state.current_page = "Applications"

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
    if "NEW_LOAN_APPLICATION:" in text:   return "system"
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

    if stage == "system" and sender_type == "User":
        return False

    data = extract_json_from_message(content)

    if stage == "pricing" and data:
        st.session_state.loan_decision = data
    if stage == "communication" and data and st.session_state.loan_decision:
        st.session_state.loan_decision = {**st.session_state.loan_decision, **data}
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
            is_testing = "streamlit.testing" in sys.modules or os.getenv("STREAMLIT_TESTING") == "true"
            if not is_testing:
                time.sleep(1.2)
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
        return

    messages = sorted(messages, key=lambda m: m.get("inserted_at") or "")

    advanced = False
    for msg in messages:
        timestamp = msg.get("inserted_at")
        if timestamp:
            st.session_state.poll_since = timestamp
        msg_id = msg.get("id")
        if msg_id is not None:
            if msg_id in st.session_state.seen_message_ids:
                continue
            st.session_state.seen_message_ids.add(msg_id)
            
        sender = msg.get("sender") or {}
        sender_type = sender.get("type") if isinstance(sender, dict) else msg.get("sender_type")
        if sender_type == "User":
            continue
        if ingest_agent_message(msg):
            advanced = True

    if advanced:
        st.rerun()


# ─────────────────────────────────────────────
# AUDIT TRAIL & HUMAN GATE HELPERS
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
    
    story.append(Paragraph("LOAN SHARK FINANCIAL SERVICES", title_style))
    story.append(Paragraph(f"Compliance Audit Trail Record — Application ID: {application_id or 'N/A'}", subtitle_style))
    story.append(Spacer(1, 8))
    
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
            
    story.append(Paragraph("Chronological Agent Processing Logs", h2_style))
    
    for idx, msg in enumerate(messages):
        stage = msg.get("stage", "system")
        sender = msg.get("sender_name", "Agent")
        timestamp = msg.get("time", "")
        text = msg.get("text", "")
        
        stage_label = {
            "doc": "Intake → Document Handoff",
            "credit": "Document → Credit Verification",
            "fraud": "Credit → Credit Analysis",
            "risk": "Credit → Fraud Assessment",
            "compliance": "Fraud → Risk Assessment",
            "decision": "Risk → Compliance Check",
            "pricing": "Compliance → Loan Decision",
            "communication": "Decision → Pricing Terms",
            "human_gate": "Pricing → Sanction Letter Draft",
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

    with st.expander("📋 Compliance Audit Trail & Regulatory Log", expanded=False):
        
        if decision:
            st.markdown("#### ⚖️ Decision Basis Summary")
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
                
            notes = decision.get("compliance_notes")
            if notes:
                st.info(f"**Regulatory Note:** {notes}")
                
            denial = decision.get("denial_reasons")
            if rec == "DENY" and denial:
                st.error("**Denial Reasons & Violations:**\n" + "\n".join(f"• {r}" for r in denial))
            
            st.divider()

        st.markdown("#### 📜 Chronological Processing Log")
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
                display_data = {k: v for k, v in json_data.items() if k not in ["letter_body", "compliance_notes"] and v is not None}
                st.json(display_data, expanded=False)
            else:
                st.text(text)
            st.markdown("---")
            
        col_json, col_pdf = st.columns(2)
        
        json_data = build_audit_json(messages, decision, application_id)
        with col_json:
            st.download_button(
                label="📥 Download JSON Record",
                data=json_data,
                file_name=f"audit_{application_id or 'loan'}.json",
                mime="application/json",
                use_container_width=True
            )
            
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
    st.markdown("#### 🔐 Human Loan Officer Review")

    badge_map = {
        "APPROVE":       ("ls-badge ls-badge-green",  "✅ APPROVE"),
        "DENY":          ("ls-badge ls-badge-red",    "❌ DENY"),
        "COUNTER_OFFER": ("ls-badge ls-badge-orange", "🔄 COUNTER OFFER"),
    }
    badge_cls, badge_text = badge_map.get(rec, ("ls-badge ls-badge-gray", rec))

    card_cls = "decision-card" if rec == "APPROVE" else ("decision-card deny" if rec == "DENY" else "decision-card counter")
    st.markdown(f"""
    <div class="{card_cls}">
        <span class="{badge_cls}">{badge_text}</span>
        <span style="color:#6b7280; font-size:0.8rem; margin-left:1rem">
            Application {decision.get('application_id', '')} &nbsp;·&nbsp; 
            Risk: {decision.get('risk_category', '')} &nbsp;·&nbsp; 
            Confidence: {decision.get('confidence', '')}
        </span>
    </div>
    """, unsafe_allow_html=True)

    is_counter_offer = (rec == "COUNTER_OFFER")
    final_amount = decision.get("approved_amount") or letter.get("approved_amount", 0.0)
    final_tenure = decision.get("approved_tenure_months") or letter.get("approved_tenure_months", 0)

    if rec in ("APPROVE", "COUNTER_OFFER") and decision:
        if is_counter_offer:
            st.markdown("##### 🛠️ Adjust Counter-Offer Terms")
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

    if letter.get("letter_body"):
        st.divider()
        st.markdown("##### 📝 Formal Letter Preview")
        letter_body = letter['letter_body']
        if is_counter_offer:
            letter_body = letter_body.replace(f"Rs {decision.get('approved_amount', 0):,}", f"Rs {final_amount:,}")
            letter_body = letter_body.replace(f"{decision.get('approved_tenure_months', 0)} Months", f"{final_tenure} Months")
            
        letter_html = letter_body.replace('\\n', '<br>').replace('\n', '<br>')
        st.markdown(f"""
        <div class="ls-card" style="font-family:'Georgia',serif; font-size:0.82rem; line-height:1.8;
             max-height:220px; overflow-y:auto; color:#374151;">
            {letter_html}
        </div>
        """, unsafe_allow_html=True)

    audit = decision.get("compliance_notes", "")
    if audit:
        with st.expander("📄 Compliance Notes Summary"):
            st.text(audit)

    st.divider()
    st.markdown("##### 👤 Loan Officer Sign-off")
    
    officer_name = st.text_input("Officer Name", value=st.session_state.get("officer_name", ""), placeholder="e.g. Navnit Nair", key="officer_name_input")
    st.session_state.officer_name = officer_name

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
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    # Logo
    st.markdown("""
    <div style="padding:1.8rem 1.2rem 1.2rem 1.2rem; border-bottom:1px solid rgba(255,255,255,0.07); margin-bottom:1rem;">
        <span style="font-size:1.5rem; font-weight:800; color:#ffffff; letter-spacing:0.5px;">LOAN<span style="color:#1dbfa0;">shark</span></span>
    </div>
    """, unsafe_allow_html=True)

    pages = [
        "⊞  Overview",
        "💳  Applications",
        "🤖  Pipeline Monitor",
        "📋  Audit Logs",
        "⚙️  Settings",
    ]

    selected_page = st.radio("nav", pages, index=1, label_visibility="collapsed")
    if selected_page != st.session_state.current_page:
        st.session_state.current_page = selected_page
        st.rerun()

    # Spacer + bottom items
    st.markdown("<div style='flex:1'></div>", unsafe_allow_html=True)
    for _ in range(8):
        st.write("")

    st.markdown("""
    <div style="padding:0.8rem 1.2rem; border-top:1px solid rgba(255,255,255,0.07);">
        <span style="color:#9ca3af; font-size:0.85rem;">→  Logout</span>
    </div>
    """, unsafe_allow_html=True)

    st.toggle("🛡️ Demo Safe Mode", value=st.session_state.get("demo_safe_mode", True), key="demo_safe_mode")

    st.markdown("""
    <div style="padding:0.8rem 1.2rem; margin-top:0.5rem; display:flex; align-items:center; gap:0.7rem;">
        <div style="width:32px;height:32px;background:#1dbfa0;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.85rem;color:#fff;font-weight:700;">L</div>
        <div>
            <div style="color:#e5e7eb; font-size:0.82rem; font-weight:600;">Loan Officer</div>
            <div style="color:#6b7280; font-size:0.72rem;">View profile</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PAGE: APPLICATIONS (FORM)
# ─────────────────────────────────────────────

def render_applications_page():
    today_str = datetime.now().strftime("%b %d, %Y")

    # Top bar
    st.markdown(f"""
    <div class="ls-topbar">
        <span class="ls-topbar-date">» {today_str}</span>
        <div class="ls-topbar-right">
            <span style="font-size:1.1rem">🔔</span>
            <input type="text" class="ls-search" placeholder="Search here">
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="ls-section-label">New Application</p>', unsafe_allow_html=True)

    # Demo quick-load row
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

    _d = DEMO_SCENARIOS.get(st.session_state.active_demo or "", {})

    with st.form("loan_form", clear_on_submit=False):

        # ── Applicant Details card ──
        st.markdown('<p class="ls-card-title" style="color:#6b7280;font-size:1rem;font-weight:600;">Applicant Details</p>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            applicant_name = st.text_input("Full Name", value=_d.get("applicant_name", ""), placeholder="Priya Sharma")
        with col2:
            applicant_age = st.number_input("Age", min_value=18, max_value=70, value=int(_d.get("applicant_age", 30)))
        with col3:
            currency = st.selectbox("Currency", ["INR", "USD"])

        col4, col5, col6 = st.columns(3)
        with col4:
            credit_score = st.number_input("Credit Score (0 if unknown)", min_value=0, max_value=900, value=int(_d.get("credit_score") or 0))
        with col5:
            emp_opts = ["salaried", "self_employed", "business_owner", "unemployed"]
            emp_default = emp_opts.index(_d["employment_type"]) if _d.get("employment_type") in emp_opts else 0
            employment_type = st.selectbox("Employment Type", emp_opts, index=emp_default)
        with col6:
            employer_name = st.text_input("Employer / Business", value=_d.get("employer_name") or "", placeholder="Infosys, Self...")

        col7, col8 = st.columns(2)
        with col7:
            monthly_income = st.number_input("Monthly Income", min_value=0.0, value=float(_d.get("monthly_income", 75000.0)), step=5000.0)
        with col8:
            years_employed = st.number_input("Years at Current Job", min_value=0.0, max_value=40.0, value=float(_d.get("years_employed", 3.0)), step=0.5)

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── Loan Request card ──
        st.markdown('<p class="ls-card-title" style="color:#6b7280;font-size:1rem;font-weight:600;">Loan Request</p>', unsafe_allow_html=True)

        col9, col10, col11 = st.columns(3)
        with col9:
            loan_amount = st.number_input("Loan Amount", min_value=10000.0, value=float(_d.get("loan_amount_requested", 500000.0)), step=10000.0)
        with col10:
            loan_opts = ["home", "vehicle", "education", "personal", "business"]
            loan_purpose_default = loan_opts.index(_d["loan_purpose"]) if _d.get("loan_purpose") in loan_opts else 0
            loan_purpose = st.selectbox("Loan Purpose", loan_opts, index=loan_purpose_default)
        with col11:
            existing_debt = st.number_input("Existing Monthly Debt", min_value=0.0, value=float(_d.get("existing_debt_monthly", 0.0)), step=1000.0)

        col12, col13 = st.columns([1, 2])
        with col12:
            loan_tenure = st.slider("Tenure (months)", min_value=6, max_value=360, value=int(_d.get("loan_tenure_months", 60)), step=6)
        with col13:
            collateral = st.text_input("Collateral Offered (optional)", placeholder="Property, Vehicle registration...")

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── Band Connection card ──
        st.markdown('<p class="ls-card-title" style="color:#6b7280;font-size:1rem;font-weight:600;">Band Connection</p>', unsafe_allow_html=True)

        bc1, bc2 = st.columns(2)
        with bc1:
            band_chat_id = st.text_input("Band Chat / Room ID", value=st.session_state.chat_id, placeholder="chat_id of your LoanShark room")
        with bc2:
            intake_handle = st.text_input("Intake Agent Handle (@mention)", value=st.session_state.intake_handle, placeholder="@yourusername/IntakeAgent")

        band_human_key = st.text_input("Band Human API Key", type="password", placeholder="Leave blank if set in .env")
        demo_safe_mode = st.session_state.get("demo_safe_mode", True)

        submitted = st.form_submit_button("🚀 Submit Application", use_container_width=True, type="primary")

    if submitted:
        if band_human_key.strip():
            os.environ["BAND_HUMAN_API_KEY"] = band_human_key.strip()
        if band_chat_id.strip():
            os.environ["BAND_CHAT_ID"] = band_chat_id.strip()

        if not demo_safe_mode and (not applicant_name or not band_chat_id.strip() or not intake_handle.strip()):
            st.error("Please fill in applicant name, Band Chat ID, and Intake Agent Handle.")
        elif not demo_safe_mode and not is_configured():
            st.error(f"Band not configured — missing: {', '.join(missing_config())}. Set BAND_HUMAN_API_KEY in .env or paste it above.")
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
            st.session_state.current_page = "🤖  Pipeline Monitor"

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
                content = f"{handle} {message}"
                try:
                    post_message(chat_id, content, mention_handle=handle)
                    st.session_state.agent_messages.append({
                        "stage": "system",
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "text": "📡 Posted to Band. Agents are processing...",
                    })
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
# PAGE: PIPELINE MONITOR
# ─────────────────────────────────────────────

def render_pipeline_page():
    today_str = datetime.now().strftime("%b %d, %Y")
    form_data = st.session_state.get("last_form_data") or st.session_state.get("loan_decision") or {}
    app_id     = st.session_state.get("application_id", "—")
    name       = form_data.get("applicant_name", "—")
    emp_type   = (form_data.get("employment_type") or "—").replace("_", " ").title()
    amt        = format_currency(form_data.get("loan_amount_requested", 0)) if form_data else "—"
    purpose    = (form_data.get("loan_purpose") or "—").title()
    status     = st.session_state.pipeline_status

    # Top bar
    st.markdown(f"""
    <div class="ls-topbar">
        <span class="ls-topbar-date">» {today_str}</span>
        <div class="ls-topbar-right">
            <span style="font-size:1.1rem">🔔</span>
            <input type="text" class="ls-search" placeholder="Search here">
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Applicant Details card ──
    st.markdown("""
    <div class="ls-card">
        <p class="ls-card-title">Applicant Details</p>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="ls-detail-grid">
            <div>
                <p class="ls-detail-label">Applicant Name</p>
                <p class="ls-detail-value">{name}</p>
            </div>
            <div>
                <p class="ls-detail-label">Employment Type</p>
                <p class="ls-detail-value">{emp_type}</p>
            </div>
            <div>
                <p class="ls-detail-label">Loan Amount</p>
                <p class="ls-detail-value">{amt}</p>
            </div>
            <div>
                <p class="ls-detail-label">Loan Purpose</p>
                <p class="ls-detail-value">{purpose}</p>
            </div>
            <div>
                <p class="ls-detail-label">Application ID</p>
                <p class="ls-detail-value">{app_id}</p>
            </div>
            <div>
                <p class="ls-detail-label">Status</p>
                <p class="ls-detail-value">{status.replace('_', ' ').title()}</p>
            </div>
        </div>
        <div class="ls-action-row">
            <span class="ls-btn-teal">View Full Application</span>
            <span class="ls-btn-ghost">Archive</span>
        </div>
    </div>
    """, unsafe_allow_html=True)



    # ── Agent Pipeline History table ──
    msgs = st.session_state.agent_messages

    # Build table rows — NO leading whitespace (markdown code-block bug)
    if not msgs:
        rows_html = '<tr><td colspan="5" style="text-align:center;color:#9ca3af;padding:2rem 0;">No active applications. Submit an application to start the pipeline.</td></tr>'
    else:
        rows_html = ""
        for msg in reversed(msgs):
            time_str = msg.get("time", "")
            stage    = msg.get("stage", "system")
            sender   = msg.get("sender_name", "Agent")
            text     = msg.get("text", "")

            if stage == "error":
                status_cls, status_lbl = "red", "Failed"
            elif stage in ("system", "thought"):
                status_cls, status_lbl = "gray", "Info"
            elif stage == "human_gate":
                status_cls, status_lbl = "blue", "Awaiting"
            else:
                status_cls, status_lbl = "green", "Complete"

            action_map = {
                "doc": "Intake", "credit": "Doc Verify", "fraud": "Credit Check",
                "risk": "Fraud Scan", "compliance": "Risk Assess", "decision": "Compliance",
                "pricing": "Decision", "communication": "Pricing", "human_gate": "Human Gate",
                "system": "System", "thought": "Thinking", "error": "Error",
            }
            action = action_map.get(stage, stage.title())

            preview = [l.strip() for l in text.split("\n") if l.strip() and not l.strip().startswith("@")]
            preview = preview[0] if preview else text[:100]
            if len(preview) > 70:
                preview = preview[:70] + "\u2026"

            # Single-line per row — no leading spaces = no markdown code-block trigger
            rows_html += f'<tr><td>{time_str}</td><td class="{status_cls}">{status_lbl}</td><td>{sender}</td><td>{action}</td><td class="bold" style="text-align:right">{preview}</td></tr>'

    # Use st.html() — bypasses the markdown parser entirely, renders raw HTML
    table_html = f"""<div class="ls-card"><p class="ls-card-title">Agent Pipeline History</p><div class="ls-table-wrap"><table class="ls-table"><thead><tr><th>Time</th><th>Status</th><th>Agent Node</th><th>Action</th><th style="text-align:right">Output Preview</th></tr></thead><tbody>{rows_html}</tbody></table></div><div class="ls-load-more-wrap"><span class="ls-load-more">Poll Latest Updates</span></div></div>"""
    st.html(table_html)

    # Auto-poll
    auto_poll_band()

    # Manual fallback
    if status == "running":
        with st.expander("📥 Manual fallback — paste an agent message"):
            st.caption("Auto-advance polls Band every 2s. Use this only if polling is unavailable.")
            agent_response = st.text_area("Paste Band room message here:", height=100, key="agent_paste")
            if st.button("Process Message", use_container_width=True):
                if agent_response:
                    ingest_agent_message(agent_response)
                    st.rerun()

    # Human gate
    if status == "awaiting_approval" and st.session_state.loan_letter:
        render_human_gate()

    # Audit trail
    render_audit_panel(st.session_state.agent_messages, st.session_state.loan_decision, st.session_state.application_id)

    # Complete
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
# PAGE: OVERVIEW (summary dashboard)
# ─────────────────────────────────────────────

def render_overview_page():
    today_str = datetime.now().strftime("%b %d, %Y")
    st.markdown(f"""
    <div class="ls-topbar">
        <span class="ls-topbar-date">» {today_str}</span>
        <div class="ls-topbar-right">
            <span style="font-size:1.1rem">🔔</span>
            <input type="text" class="ls-search" placeholder="Search here">
        </div>
    </div>
    """, unsafe_allow_html=True)

    msgs   = st.session_state.agent_messages
    status = st.session_state.pipeline_status

    approved_count  = sum(1 for m in msgs if m.get("stage") == "pricing")
    pipeline_active = 1 if status == "running" else 0
    total_apps      = 1 if st.session_state.application_id else 0

    st.markdown(f"""
    <div class="ls-card">
        <p class="ls-card-title">System Overview</p>
        <div class="ls-detail-grid">
            <div>
                <p class="ls-detail-label">Total Applications</p>
                <p class="ls-detail-value">{total_apps}</p>
            </div>
            <div>
                <p class="ls-detail-label">Pipeline Active</p>
                <p class="ls-detail-value">{pipeline_active}</p>
            </div>
            <div>
                <p class="ls-detail-label">Decisions Made</p>
                <p class="ls-detail-value">{approved_count}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    rows = ""
    for msg in (msgs[-10:] if len(msgs) > 10 else msgs):
        stage = msg.get("stage", "system")
        sc = "green" if stage not in ("error", "system") else ("red" if stage == "error" else "gray")
        lbl = "Complete" if stage not in ("error", "system") else ("Failed" if stage == "error" else "Info")
        sender = msg.get("sender_name", "Agent")
        t = msg.get("time", "")
        txt = msg.get("text", "")[:60] + ("…" if len(msg.get("text","")) > 60 else "")
        rows += f"""
        <tr>
            <td>{t}</td>
            <td class="{sc}">{lbl}</td>
            <td>{sender}</td>
            <td class="bold" style="text-align:right">{txt}</td>
        </tr>
        """

    if not rows:
        rows = '<tr><td colspan="4" style="text-align:center;color:#9ca3af;padding:2rem 0;">No activity yet. Submit an application to begin.</td></tr>'

    st.markdown(f"""
    <div class="ls-card">
        <p class="ls-card-title">Recent Activity</p>
        <div class="ls-table-wrap">
            <table class="ls-table">
                <thead>
                    <tr><th>Time</th><th>Status</th><th>Agent</th><th style="text-align:right">Detail</th></tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────

page = st.session_state.current_page

if page == "💳  Applications":
    # Store last form data for pipeline page
    render_applications_page()
elif page == "🤖  Pipeline Monitor":
    render_pipeline_page()
elif page == "⊞  Overview":
    render_overview_page()
else:
    today_str = datetime.now().strftime("%b %d, %Y")
    st.markdown(f"""
    <div class="ls-topbar">
        <span class="ls-topbar-date">» {today_str}</span>
        <div class="ls-topbar-right">
            <span style="font-size:1.1rem">🔔</span>
            <input type="text" class="ls-search" placeholder="Search here">
        </div>
    </div>
    <div class="ls-card" style="text-align:center; color:#9ca3af; padding:3rem;">
        <p style="font-size:1.1rem; font-weight:600; color:#374151; margin-bottom:0.5rem;">Coming Soon</p>
        <p>This section is not yet implemented in the demo.</p>
    </div>
    """, unsafe_allow_html=True)

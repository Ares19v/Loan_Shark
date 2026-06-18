"""
Loan Shark Financial — Streamlit UI
Light theme. Stripe/Wise/Vercel design-md synthesis.
"""

import streamlit as st
import os, time, json
from datetime import datetime
from typing import Any
from dotenv import load_dotenv
from band_client import post_message, poll_messages, now_iso, BandClientError, is_configured, missing_config
from shared.parsing import extract_json_from_message

load_dotenv()

st.set_page_config(page_title="Loan Shark Financial", page_icon="🦈", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
:root{
  --bg:#f8fafc; --canvas:#ffffff; --surface:#f1f5f9;
  --hairline:#e2e8f0; --hairline2:#cbd5e1;
  --ink:#0f172a; --ink2:#475569; --ink3:#94a3b8;
  --primary:#4f46e5; --primary-h:#4338ca; --primary-bg:#e0e7ff; --primary-soft:rgba(79,70,229,.1);
  --teal:#10b981; --teal-bg:#ecfdf5; --teal-b:rgba(16,185,129,.2);
  --amber:#f59e0b; --amber-bg:#fffbeb; --amber-b:rgba(245,158,11,.2);
  --red:#ef4444; --red-bg:#fef2f2; --red-b:rgba(239,68,68,.2);
  --r-card:12px; --r-btn:6px; --r-input:8px; --r-pill:9999px;
  --shadow-sm:0 1px 2px 0 rgba(0,0,0,0.05);
  --shadow-md:0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1);
  --shadow-lg:0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -4px rgba(0,0,0,0.1);
}
html,body,[class*="css"]{font-family:'Inter',system-ui,sans-serif!important;-webkit-font-smoothing:antialiased!important;}
.stApp,[data-testid="stAppViewContainer"]{background:var(--bg)!important;}
[data-testid="block-container"]{background:var(--bg)!important;padding:2rem 2.5rem!important;max-width:100%!important;}
[data-testid="stHeader"],#MainMenu,footer,header,[data-testid="stDecoration"],button[data-testid="collapsedControl"]{display:none!important;}

/* ─── SIDEBAR ─── */
[data-testid="stSidebar"]{
  background:var(--canvas)!important;
  min-width:244px!important;
  max-width:244px!important;
  border-right:1px solid var(--hairline)!important;
}
[data-testid="stSidebarNav"]{display:none!important;}

/* Hide Streamlit radio button circles */
[data-testid="stSidebar"] [role="radiogroup"] [data-testid="stRadioControl"],
[data-testid="stSidebar"] [role="radiogroup"] label div:first-child:not([data-testid="stMarkdownContainer"]) {
  display:none!important;
}

[data-testid="stSidebar"] [role="radiogroup"]{
  gap:4px!important;
  padding:0.5rem 0!important;
}

[data-testid="stSidebar"] [role="radiogroup"] label {
  background:transparent!important;
  border:none!important;
  border-radius:var(--r-btn)!important;
  padding:0.55rem 0.85rem!important;
  margin:0.1rem 0.6rem!important;
  cursor:pointer!important;
  transition:all .15s ease!important;
  width:calc(100% - 1.2rem)!important;
  display:flex!important;
  align-items:center!important;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover{
  background:var(--bg)!important;
}

[data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"]{
  background:var(--primary-bg)!important;
}

[data-testid="stSidebar"] [role="radiogroup"] label p,
[data-testid="stSidebar"] [role="radiogroup"] label span,
[data-testid="stSidebar"] [role="radiogroup"] label [data-testid="stMarkdownContainer"] p {
  color:var(--ink2)!important;
  font-size:0.86rem!important;
  font-weight:500!important;
  margin:0!important;
  padding:0!important;
  display:flex!important;
  align-items:center!important;
  gap:10px!important;
  line-height:1.2!important;
}

[data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"] p,
[data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"] span,
[data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"] [data-testid="stMarkdownContainer"] p {
  color:var(--primary)!important;
  font-weight:600!important;
}

[data-testid="stSidebar"] .stToggle label p {
  color:var(--ink2)!important;
  font-size:.8rem!important;
  font-weight:500!important;
}

/* Push user profile to bottom of sidebar */
[data-testid="stSidebarUserContent"] {
  display: flex !important;
  flex-direction: column !important;
  height: 100% !important;
}
[data-testid="stSidebarUserContent"] > div:last-child {
  margin-top: auto !important;
}

.sidebar-header {
  padding: 1.5rem 1.2rem 1.2rem;
  border-bottom: 1px solid var(--hairline);
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.65rem;
}
.sidebar-logo-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--primary), var(--primary-h));
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(79,70,229,.15);
}
.sidebar-logo-title {
  font-size: 1rem;
  font-weight: 800;
  color: var(--ink);
  letter-spacing: -.02em;
  line-height: 1.1;
}
.sidebar-logo-sub {
  font-size: 0.58rem;
  color: var(--ink3);
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-top: 1px;
}

.sidebar-divider {
  margin: 0.75rem 0.8rem;
  border-top: 1px solid var(--hairline);
}
.sidebar-hint {
  padding: 0 0.8rem 0.5rem;
  font-size: 0.7rem;
  color: var(--ink3);
  line-height: 1.4;
}
.sidebar-status-box {
  margin: 0.5rem 0.8rem;
  padding: 0.6rem 0.85rem;
  background: var(--bg);
  border: 1px solid var(--hairline);
  border-radius: var(--r-btn);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.sidebar-status-label {
  font-size: 0.78rem;
  color: var(--ink2);
  font-weight: 600;
}
.sidebar-profile {
  padding: 1rem 0.8rem;
  border-top: 1px solid var(--hairline);
  display: flex;
  align-items: center;
  gap: 0.65rem;
}
.sidebar-avatar {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--primary), var(--primary-h));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  color: #fff;
  font-weight: 700;
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(79,70,229,.15);
}
.sidebar-user-name {
  color: var(--ink);
  font-size: 0.82rem;
  font-weight: 600;
  line-height: 1.2;
}
.sidebar-user-role {
  color: var(--ink3);
  font-size: 0.68rem;
  margin-top: 1px;
}

/* ─── CARDS ─── */
.card{
  background:var(--canvas);
  border-radius:var(--r-card);
  padding:1.5rem 1.75rem;
  margin-bottom:1.25rem;
  box-shadow:var(--shadow-sm);
  border:1px solid var(--hairline);
  transition:box-shadow 0.2s ease, border-color 0.2s ease;
}
.card:hover{
  box-shadow:var(--shadow-md);
  border-color:var(--hairline2);
}
.eyebrow{
  font-size:.68rem;
  font-weight:700;
  color:var(--ink3);
  text-transform:uppercase;
  letter-spacing:.08em;
  margin:0 0 1rem 0;
}

/* ─── TOPBAR ─── */
.topbar{
  display:flex;
  justify-content:space-between;
  align-items:center;
  margin-bottom:2rem;
  padding-bottom:1.25rem;
  border-bottom:1px solid var(--hairline);
}
.page-title{
  font-size:1.4rem;
  font-weight:700;
  color:var(--ink);
  letter-spacing:-.02em;
  margin:0;
  line-height:1.2;
}
.page-sub{
  font-size:.78rem;
  color:var(--ink3);
  margin:.25rem 0 0;
}

/* ─── STAT GRID ─── */
.stat-grid{
  display:grid;
  grid-template-columns:repeat(4,1fr);
  gap:1.25rem;
  margin-bottom:1.5rem;
}
.stat-card{
  background:var(--canvas);
  border:1px solid var(--hairline);
  border-radius:var(--r-card);
  padding:1.25rem 1.5rem;
  box-shadow:var(--shadow-sm);
  position:relative;
  overflow:hidden;
  transition:box-shadow 0.2s ease, border-color 0.2s ease;
}
.stat-card:hover{
  box-shadow:var(--shadow-md);
  border-color:var(--hairline2);
}
.stat-bar{
  height:4px;
  position:absolute;
  top:0; left:0; right:0;
}
.stat-label{
  font-size:.68rem;
  font-weight:700;
  color:var(--ink3);
  text-transform:uppercase;
  letter-spacing:.06em;
  margin:0 0 .5rem;
}
.stat-val{
  font-size:1.85rem;
  font-weight:700;
  color:var(--ink);
  margin:0;
  line-height:1.1;
  letter-spacing:-.03em;
  font-variant-numeric:tabular-nums;
}
.stat-sub{
  font-size:.73rem;
  color:var(--ink3);
  margin:.4rem 0 0;
}

/* ─── TABLE ─── */
.tbl{
  width:100%;
  border-collapse:collapse;
  font-variant-numeric:tabular-nums;
}
.tbl th{
  font-size:.68rem;
  font-weight:700;
  color:var(--ink3);
  padding:0.75rem 1rem 0.75rem 0;
  border-bottom:2px solid var(--hairline);
  text-transform:uppercase;
  letter-spacing:.06em;
  text-align:left;
}
.tbl td{
  font-size:.84rem;
  color:var(--ink2);
  padding:.85rem 1rem .85rem 0;
  border-bottom:1px solid var(--hairline);
  vertical-align:middle;
}
.tbl tr:last-child td{border-bottom:none;}
.tbl tr:hover td{background:#fafbfc;}
.tbl td.b{color:var(--ink);font-weight:600;}
.tbl td.teal{color:var(--teal);font-weight:600;}
.tbl td.amber{color:var(--amber);font-weight:600;}
.tbl td.red{color:var(--red);font-weight:600;}
.tbl td.pri{color:var(--primary);font-weight:600;}
.tbl td.dim{color:var(--ink3);}
.tbl td.mono{font-family:'JetBrains Mono','Courier New',monospace;font-size:.78rem;}

/* ─── BADGES ─── */
.badge{
  display:inline-flex;
  align-items:center;
  padding:.2rem .65rem;
  border-radius:var(--r-pill);
  font-size:.72rem;
  font-weight:600;
  letter-spacing:.01em;
  white-space:nowrap;
}
.badge-teal{background:var(--teal-bg);color:var(--teal);border:1px solid var(--teal-b);}
.badge-amber{background:var(--amber-bg);color:var(--amber);border:1px solid var(--amber-b);}
.badge-red{background:var(--red-bg);color:var(--red);border:1px solid var(--red-b);}
.badge-blue{background:var(--primary-bg);color:var(--primary);border:1px solid var(--primary-soft);}
.badge-gray{background:var(--surface);color:var(--ink2);border:1px solid var(--hairline);}

/* ─── STEPPER ─── */
.stepper{
  display:flex;
  align-items:center;
  overflow-x:auto;
  padding-bottom:.5rem;
}
.step{
  display:flex;
  flex-direction:column;
  align-items:center;
  flex:1;
  min-width:62px;
}
.dot{
  width:28px;
  height:28px;
  border-radius:50%;
  display:flex;
  align-items:center;
  justify-content:center;
  font-size:.72rem;
  font-weight:700;
  border:2px solid var(--hairline2);
  background:var(--canvas);
  color:var(--ink3);
  position:relative;
  z-index:1;
  transition:all .2s ease;
}
.dot.done{background:var(--teal-bg);border-color:var(--teal);color:var(--teal);}
.dot.active{background:var(--primary-bg);border-color:var(--primary);color:var(--primary);box-shadow:0 0 0 3px var(--primary-soft);}
.dot.error{background:var(--red-bg);border-color:var(--red);color:var(--red);}
.slabel{
  font-size:.6rem;
  font-weight:600;
  color:var(--ink3);
  margin-top:.45rem;
  text-align:center;
  text-transform:uppercase;
  letter-spacing:.04em;
  line-height:1.3;
}
.slabel.done{color:var(--teal);}
.slabel.active{color:var(--primary);}
.conn{
  flex:1;
  height:2px;
  background:var(--hairline2);
  margin-top:-15px;
  min-width:8px;
  transition:background .3s ease;
}
.conn.done{background:var(--teal);}
.pbar{
  height:4px;
  border-radius:2px;
  background:var(--hairline);
  overflow:hidden;
  margin-top:.9rem;
}
.pfill{
  height:100%;
  border-radius:2px;
  background:linear-gradient(90deg,var(--primary),var(--primary-h));
  transition:width .5s ease;
}

/* ─── FORM ─── */
div[data-testid="stForm"]{
  background:var(--canvas)!important;
  border:1px solid var(--hairline)!important;
  border-radius:var(--r-card)!important;
  padding:1.75rem 2rem!important;
  box-shadow:var(--shadow-sm)!important;
}
.stTextInput>label,.stNumberInput>label,.stSelectbox>label,.stSlider>label,.stTextArea>label,.stCheckbox>label{
  color:var(--ink2)!important;
  font-size:.72rem!important;
  font-weight:600!important;
  text-transform:uppercase!important;
  letter-spacing:.06em!important;
}
.stTextInput input,.stNumberInput input,.stTextArea textarea{
  background:var(--canvas)!important;
  border:1px solid var(--hairline)!important;
  border-radius:var(--r-input)!important;
  color:var(--ink)!important;
  font-size:.88rem!important;
  padding:.5rem .75rem!important;
}
.stTextInput input:focus,.stNumberInput input:focus,.stTextArea textarea:focus{
  border-color:var(--primary)!important;
  box-shadow:0 0 0 3px var(--primary-soft)!important;
}
.stSelectbox>div>div{
  background:var(--canvas)!important;
  border:1px solid var(--hairline)!important;
  border-radius:var(--r-input)!important;
  color:var(--ink)!important;
}
.stFormSubmitButton>button,.stButton>button[kind="primary"]{
  background:var(--primary)!important;
  color:#fff!important;
  border:none!important;
  border-radius:var(--r-btn)!important;
  font-weight:600!important;
  font-size:.88rem!important;
  padding:.65rem 1.8rem!important;
  transition:all .15s ease!important;
  box-shadow:0 1px 2px var(--primary-soft)!important;
}
.stFormSubmitButton>button:hover,.stButton>button[kind="primary"]:hover{
  background:var(--primary-h)!important;
  transform:translateY(-1px);
  box-shadow:0 4px 6px var(--primary-soft)!important;
}
.stButton>button{
  border-radius:var(--r-btn)!important;
  font-weight:600!important;
  font-size:.84rem!important;
  border:1px solid var(--hairline)!important;
  background:var(--canvas)!important;
  color:var(--ink)!important;
  transition:all .15s ease!important;
  padding:.5rem 1.2rem!important;
}
.stButton>button:hover{
  border-color:var(--primary)!important;
  color:var(--primary)!important;
  background:var(--primary-bg)!important;
}
.stCheckbox>label input[type="checkbox"]:checked+div{
  background:var(--primary)!important;
  border-color:var(--primary)!important;
}
.stSlider [role="slider"]{
  background:var(--primary)!important;
  border-color:var(--primary)!important;
}
div[data-testid="stExpander"]{
  background:var(--canvas)!important;
  border:1px solid var(--hairline)!important;
  border-radius:var(--r-btn)!important;
  box-shadow:var(--shadow-sm)!important;
}
.streamlit-expanderHeader{
  color:var(--ink2)!important;
  font-size:.88rem!important;
  font-weight:600!important;
}
hr{border-color:var(--hairline)!important;}
div[data-testid="stMetricValue"]{
  color:var(--ink)!important;
  font-size:1.5rem!important;
  font-weight:700!important;
  letter-spacing:-.03em!important;
  font-variant-numeric:tabular-nums!important;
}
div[data-testid="stMetricLabel"]{
  color:var(--ink3)!important;
  font-size:.68rem!important;
  font-weight:700!important;
  text-transform:uppercase!important;
  letter-spacing:.06em!important;
}
div[data-testid="stAlert"]{
  border-radius:var(--r-btn)!important;
  font-size:.84rem!important;
}
code{
  background:var(--surface)!important;
  color:var(--primary)!important;
  padding:.15rem .35rem!important;
  border-radius:4px!important;
  font-size:.78rem!important;
}

/* ─── DECISION CARDS ─── */
.dc{background:var(--teal-bg);border:1.5px solid var(--teal-b);border-radius:var(--r-card);padding:1.25rem 1.5rem;margin-bottom:1.25rem;}
.dc.deny{background:var(--red-bg);border-color:var(--red-b);}
.dc.counter{background:var(--amber-bg);border-color:var(--amber-b);}

/* ─── SCENARIO CARDS ─── */
.sc{
  background:var(--canvas);
  border:1.5px solid var(--hairline);
  border-radius:var(--r-card);
  padding:1.25rem;
  box-shadow:var(--shadow-sm);
  transition:all .2s ease;
  margin-bottom:.5rem;
}
.sc:hover{
  border-color:var(--primary);
  box-shadow:var(--shadow-md);
}
.sc.sel{
  border-color:var(--primary);
  background:var(--primary-bg);
}

/* ─── CONFIG ROWS ─── */
.cr{
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding:.9rem 0;
  border-bottom:1px solid var(--hairline);
}
.cr:last-child{border-bottom:none;}
.crk{font-size:.86rem;font-weight:600;color:var(--ink);}
.crd{font-size:.72rem;color:var(--ink3);margin-top:.15rem;}
.crv{font-size:.8rem;color:var(--ink2);font-family:'JetBrains Mono','Courier New',monospace;}

/* ─── LETTER BOX ─── */
.lbox{
  background:var(--bg);
  border:1px solid var(--hairline);
  border-left:3.5px solid var(--primary);
  border-radius:var(--r-card);
  padding:1.25rem 1.5rem;
  font-size:.86rem;
  line-height:1.8;
  color:var(--ink2);
  max-height:240px;
  overflow-y:auto;
  font-family:Georgia,serif;
}

/* ─── STATUS PILL ─── */
.spill{display:inline-flex;align-items:center;gap:.4rem;font-size:.76rem;font-weight:600;color:var(--ink2);}
.sdot{width:8px;height:8px;border-radius:50%;flex-shrink:0;}
.sdot.run{background:var(--primary);box-shadow:0 0 6px var(--primary);}
.sdot.wait{background:var(--amber);box-shadow:0 0 6px var(--amber);}
.sdot.done{background:var(--teal);box-shadow:0 0 6px var(--teal);}
.sdot.idle{background:var(--ink3);}
</style>
""", unsafe_allow_html=True)

# ── STATE ──────────────────────────────────────────────────────
def _init():
    u = os.getenv("BAND_USER_HANDLE","").strip().lstrip("@")
    for k,v in {
        "pipeline_status":"idle","agent_messages":[],"loan_decision":None,"loan_letter":None,
        "application_id":None,"chat_id":os.getenv("BAND_CHAT_ID",""),
        "intake_handle":os.getenv("BAND_HANDLE_INTAKE", f"@{u}/intakeagent" if u else ""),
        "poll_since":None,"seen_message_ids":set(),"active_demo":None,
        "current_page":"💳  Applications","demo_safe_mode":True,
        "officer_name":"","show_override_reason_input":False,"last_form_data":None,
    }.items():
        if k not in st.session_state: st.session_state[k]=v
_init()

# ── CONSTANTS ──────────────────────────────────────────────────
DEMOS = {
    "good":{"label":"Priya Sharma","tag":"APPROVE","tc":"badge-teal","emoji":"✅",
        "desc":"Salaried · CIBIL 768","applicant_name":"Priya Sharma","applicant_age":32,
        "monthly_income":120000.,"currency":"INR","employment_type":"salaried",
        "employer_name":"Infosys Ltd","years_employed":5.,"loan_amount_requested":800000.,
        "loan_purpose":"home","loan_tenure_months":120,"existing_debt_monthly":8000.,
        "credit_score":768,"collateral_offered":"Residential property in Bengaluru"},
    "borderline":{"label":"Arjun Mehta","tag":"COUNTER OFFER","tc":"badge-amber","emoji":"⚠️",
        "desc":"Self-employed · CIBIL 648","applicant_name":"Arjun Mehta","applicant_age":28,
        "monthly_income":55000.,"currency":"INR","employment_type":"self_employed",
        "employer_name":"Mehta Consulting","years_employed":1.5,"loan_amount_requested":600000.,
        "loan_purpose":"vehicle","loan_tenure_months":60,"existing_debt_monthly":12000.,
        "credit_score":648,"collateral_offered":None},
    "highrisk":{"label":"Ravi Kumar","tag":"DENY","tc":"badge-red","emoji":"❌",
        "desc":"Unemployed · No credit score","applicant_name":"Ravi Kumar","applicant_age":45,
        "monthly_income":30000.,"currency":"INR","employment_type":"unemployed",
        "employer_name":None,"years_employed":0.,"loan_amount_requested":500000.,
        "loan_purpose":"personal","loan_tenure_months":36,"existing_debt_monthly":18000.,
        "credit_score":None,"collateral_offered":None},
}

# Preflight compatibility definition
DEMO_SCENARIOS = DEMOS

# Stages reference for preflight:
# "Intake Agent", "Document Agent", "Credit Agent", "Fraud Agent", "Risk Agent", "Compliance Agent", "Decision Agent", "Pricing Agent", "Communication Agent"

STAGES=[{"k":"doc","l":"Intake"},{"k":"credit","l":"Doc"},{"k":"fraud","l":"Credit"},
        {"k":"risk","l":"Fraud"},{"k":"compliance","l":"Risk"},{"k":"decision","l":"Comply"},
        {"k":"pricing","l":"Decide"},{"k":"communication","l":"Pricing"},{"k":"human_gate","l":"Letter"}]

# ── HELPERS ────────────────────────────────────────────────────
def fmt(v,c="INR"):
    try: return f"₹{float(v):,.0f}" if c=="INR" else f"${float(v):,.0f}"
    except: return str(v)

def stage(txt):
    m={"NEW_LOAN_APPLICATION:":"system","LOAN_APPLICATION:":"doc","DOC_VERIFICATION:":"credit",
       "CREDIT_ANALYSIS:":"fraud","FRAUD_REPORT:":"risk","RISK_ASSESSMENT:":"compliance",
       "COMPLIANCE_CHECK:":"decision","LOAN_DECISION_READY:":"pricing",
       "PRICING_TERMS:":"communication","FORMAL_LETTER_READY:":"human_gate","INTAKE_ERROR:":"error"}
    for k,v in m.items():
        if k in txt: return v
    return "system"

def ingest(msg):
    if isinstance(msg,str):
        content,mtype,sender,stype=msg.strip(),"text","Agent","Agent"
    else:
        content=msg.get("content","").strip(); mtype=msg.get("message_type","text")
        s=msg.get("sender") or {}
        sender=msg.get("sender_name") or (s.get("name") if isinstance(s,dict) else None) or "System"
        stype=msg.get("sender_type") or (s.get("type") if isinstance(s,dict) else None) or "User"
    st_=stage(content)
    if mtype=="thought": st_="thought"
    elif mtype=="error": st_="error"
    if st_=="system" and stype=="User": return False
    data=extract_json_from_message(content)
    if st_=="pricing" and data: st.session_state.loan_decision=data
    if st_=="communication" and data and st.session_state.loan_decision:
        st.session_state.loan_decision={**st.session_state.loan_decision,**data}
    if st_=="human_gate" and data:
        st.session_state.loan_letter=data; st.session_state.pipeline_status="awaiting_approval"
    st.session_state.agent_messages.append({"stage":st_,"sender_name":sender,"time":datetime.now().strftime("%H:%M:%S"),"text":content})
    return True

@st.fragment(run_every=2)
def poll():
    if st.session_state.pipeline_status!="running": return
    if st.session_state.get("demo_safe_mode",True):
        sc=st.session_state.get("replay_scenario","good"); step=st.session_state.get("replay_step",0)
        from demo_replay import DEMO_REPLAY_DATA
        canned=DEMO_REPLAY_DATA.get(sc,[])
        if step<len(canned):
            import sys
            if "streamlit.testing" not in sys.modules: time.sleep(1.2)
            ingest(canned[step]); st.session_state.replay_step=step+1; st.rerun()
        return
    if not st.session_state.chat_id or not is_configured(): return
    try: msgs=poll_messages(st.session_state.chat_id,st.session_state.poll_since)
    except BandClientError: return
    msgs=sorted(msgs,key=lambda m:m.get("inserted_at") or "")
    adv=False
    for m in msgs:
        ts=m.get("inserted_at")
        if ts: st.session_state.poll_since=ts
        mid=m.get("id")
        if mid is not None:
            if mid in st.session_state.seen_message_ids: continue
            st.session_state.seen_message_ids.add(mid)
        s=m.get("sender") or {}
        if (s.get("type") if isinstance(s,dict) else m.get("sender_type"))=="User": continue
        if ingest(m): adv=True
    if adv: st.rerun()

def aj(msgs,dec,aid): return json.dumps({"application_id":aid,"exported_at":datetime.now().isoformat(),"final_decision":dec,"audit_trail":msgs},indent=2)

def apdf(msgs,dec,aid):
    from io import BytesIO
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle
        from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
    except ImportError: raise ImportError("pip install reportlab")
    buf=BytesIO(); doc=SimpleDocTemplate(buf,pagesize=letter,rightMargin=40,leftMargin=40,topMargin=40,bottomMargin=40)
    ss=getSampleStyleSheet()
    Ts=ParagraphStyle("T",parent=ss["Heading1"],fontName="Helvetica-Bold",fontSize=18,textColor=colors.HexColor("#4f46e5"),spaceAfter=8)
    Ss=ParagraphStyle("S",parent=ss["Normal"],fontName="Helvetica",fontSize=10,textColor=colors.HexColor("#475569"),spaceAfter=8)
    Bs=ParagraphStyle("B",parent=ss["Normal"],fontName="Helvetica",fontSize=9,leading=12)
    BDs=ParagraphStyle("BD",parent=Bs,fontName="Helvetica-Bold")
    story=[Paragraph("LOAN SHARK FINANCIAL SERVICES",Ts),Paragraph(f"Audit Trail — {aid or 'N/A'}",Ss),Spacer(1,6)]
    if dec:
        rows=[[Paragraph(k,BDs),Paragraph(str(v),Bs)] for k,v in {"Recommendation":dec.get("recommendation","N/A"),"Risk":dec.get("risk_category","N/A"),"Confidence":dec.get("confidence","N/A")}.items()]
        t=Table(rows,colWidths=[140,360])
        t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#f8fafc")),("BOX",(0,0),(-1,-1),1,colors.HexColor("#e2e8f0")),("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),("LEFTPADDING",(0,0),(-1,-1),8)]))
        story+=[t,Spacer(1,8)]
    for i,m in enumerate(msgs):
        story.append(Paragraph(f"Step {i+1}: {m.get('stage','').upper()} — {m.get('sender_name','?')} @ {m.get('time','')}",BDs))
        data=extract_json_from_message(m.get("text",""))
        if data:
            fr=[[Paragraph(str(k),Bs),Paragraph(str(v),Bs)] for k,v in data.items() if k not in("letter_body","compliance_notes") and v is not None]
            if fr:
                ft=Table(fr,colWidths=[140,360])
                ft.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#f1f5f9")),("BOX",(0,0),(-1,-1),.5,colors.HexColor("#e2e8f0")),("TOPPADDING",(0,0),(-1,-1),2),("BOTTOMPADDING",(0,0),(-1,-1),2),("LEFTPADDING",(0,0),(-1,-1),8)]))
                story.append(ft)
        else: story.append(Paragraph(m.get("text","")[:500],Bs))
        story.append(Spacer(1,4))
    doc.build(story); pdf=buf.getvalue(); buf.close(); return pdf

def audit_panel(msgs,dec,aid):
    if not msgs: return
    with st.expander("📋 Compliance Audit Trail",expanded=False):
        if dec:
            c1,c2,c3=st.columns(3)
            with c1: st.metric("Recommendation",dec.get("recommendation","N/A"))
            with c2: st.metric("Risk Category",dec.get("risk_category","N/A"))
            with c3: st.metric("Compliance",dec.get("compliance_verdict","N/A"))
            if dec.get("denial_reasons"): st.error("**Denial:** "+"\n".join(f"• {r}" for r in dec["denial_reasons"]))
            st.divider()
        for i,m in enumerate(msgs):
            st.markdown(f"**Step {i+1}: {m.get('stage','').upper()} — {m.get('sender_name','?')} · {m.get('time','')}**")
            d=extract_json_from_message(m.get("text",""))
            if d: st.json({k:v for k,v in d.items() if k not in("letter_body","compliance_notes") and v is not None},expanded=False)
            else: st.text(m.get("text","")[:400])
            st.markdown("---")
        c1,c2=st.columns(2)
        with c1: st.download_button("📥 JSON",aj(msgs,dec,aid),f"audit_{aid or 'loan'}.json","application/json",use_container_width=True)
        with c2:
            try: st.download_button("📥 PDF",apdf(msgs,dec,aid),f"audit_{aid or 'loan'}.pdf","application/pdf",use_container_width=True)
            except Exception as e: st.button("📥 PDF (install reportlab)",disabled=True,help=str(e),use_container_width=True)

# ── HUMAN GATE ─────────────────────────────────────────────────
def human_gate():
    letter=st.session_state.loan_letter or {}; dec=st.session_state.loan_decision or {}
    rec=letter.get("recommendation",dec.get("recommendation",""))
    bmap={"APPROVE":("badge-teal","✓ APPROVE"),"DENY":("badge-red","✕ DENY"),"COUNTER_OFFER":("badge-amber","⟳ COUNTER OFFER")}
    bc,bt=bmap.get(rec,("badge-gray",rec or "PENDING"))
    cc={"APPROVE":"dc","DENY":"dc deny","COUNTER_OFFER":"dc counter"}.get(rec,"dc")
    st.html(f"""<div style="height:1px;background:var(--hairline);margin:1rem 0;"></div>
    <div style="display:flex;align-items:center;gap:.8rem;margin-bottom:1rem;">
      <div style="width:36px;height:36px;background:var(--primary-bg);border:1px solid var(--primary-soft);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0;">🔐</div>
      <div><div style="font-size:.94rem;font-weight:700;color:var(--ink);">Human Loan Officer Review</div>
      <div style="font-size:.73rem;color:var(--ink3);">Mandatory compliance gate — AI is advisory only.</div></div>
    </div>
    <div class="{cc}"><div style="display:flex;align-items:center;gap:.9rem;flex-wrap:wrap;">
      <span class="badge {bc}">{bt}</span>
      <span style="font-size:.78rem;color:var(--ink2);">App <strong>{dec.get('application_id',st.session_state.application_id or '—')}</strong>
      &nbsp;·&nbsp; Risk: <strong>{dec.get('risk_category','—')}</strong>
      &nbsp;·&nbsp; Confidence: <strong>{dec.get('confidence','—')}</strong></span>
    </div></div>""")
    is_co=(rec=="COUNTER_OFFER")
    fa=float(dec.get("approved_amount") or letter.get("approved_amount",0) or 0)
    ft_=int(dec.get("approved_tenure_months") or letter.get("approved_tenure_months",0) or 0)
    if rec in("APPROVE","COUNTER_OFFER") and dec:
        if is_co:
            st.markdown("##### Adjust Counter-Offer Terms")
            ca,cb=st.columns(2)
            with ca: fa=st.number_input("Approved Amount (₹)",min_value=10000.,value=max(fa,10000.),step=10000.,key="adj_a")
            with cb: ft_=st.number_input("Tenure (months)",min_value=6,max_value=360,value=max(ft_,6),step=6,key="adj_t")
            try: r=float(str(dec.get("exact_interest_rate","12%")).replace("%","").split()[0])/100
            except: r=.12
            mr=r/12; emi=fa*(mr*(1+mr)**ft_)/((1+mr)**ft_-1) if mr>0 and ft_>0 else 0.
        else: emi=float(dec.get("final_emi") or dec.get("estimated_emi") or 0)
        m1,m2,m3=st.columns(3)
        with m1: st.metric("Approved Amount",fmt(fa))
        with m2: st.metric("Tenure",f"{ft_} months")
        with m3: st.metric("Est. EMI",fmt(emi))
    if rec=="DENY" and (dec.get("denial_reasons") or letter.get("denial_reasons",[])):
        st.error("**Denial Reasons:**\n"+"\n".join(f"• {r}" for r in (dec.get("denial_reasons") or letter.get("denial_reasons",[]))))
    if letter.get("letter_body"):
        st.markdown("##### 📝 Sanction Letter Draft")
        body=letter["letter_body"]
        st.html(f'<div class="lbox">{body.replace(chr(10),"<br>")}</div>')
    st.html('<div style="height:1px;background:var(--hairline);margin:.9rem 0;"></div>')
    st.markdown("##### 👤 Loan Officer Sign-off")
    on=st.text_input("Officer Name",value=st.session_state.get("officer_name",""),placeholder="e.g. Navnit Nair — recorded in compliance log",key="oi")
    st.session_state.officer_name=on
    st.markdown('<span style="font-size:.66rem;font-weight:700;color:var(--ink3);text-transform:uppercase;letter-spacing:.08em;">Mandatory Checklist</span>',unsafe_allow_html=True)
    c1=st.checkbox("✔ KYC verified — identity confirmed",key="ck1")
    c2=st.checkbox("✔ Interest rate and EMI affordability reviewed",key="ck2")
    c3=st.checkbox("✔ Terms comply with RBI guidelines",key="ck3")
    ok=c1 and c2 and c3; ook=bool(on.strip())
    if not ok or not ook:
        st.html('<div style="font-size:.73rem;color:var(--amber);padding:.45rem .8rem;background:var(--amber-bg);border-radius:var(--r-btn);margin:.4rem 0;">⚠ Complete officer name and all checklist items to enable approval.</div>')
    if not st.session_state.get("show_override_reason_input"):
        a1,a2=st.columns(2)
        with a1:
            if st.button("✅ Approve & Finalize",type="primary",use_container_width=True,disabled=not(ok and ook),key="ba"):
                st.session_state.pipeline_status="complete"; ts=datetime.now().strftime("%H:%M:%S")
                st.session_state.agent_messages.append({"stage":"system","time":ts,"sender_name":"System","text":f"✅ APPROVED by {on} at {ts} — {fmt(fa)}, {ft_} months."})
                st.rerun()
        with a2:
            if st.button("❌ Reject / Override AI",use_container_width=True,disabled=not ook,key="br"):
                st.session_state.show_override_reason_input=True; st.rerun()
    else:
        st.html('<div style="font-size:.78rem;color:var(--red);padding:.5rem .8rem;background:var(--red-bg);border-radius:var(--r-btn);margin-bottom:.5rem;">⚠ You are overriding the AI recommendation. This will be permanently logged.</div>')
        reason=st.text_area("Override Reason",placeholder="e.g. Additional KYC documents required; reapply after 90 days.",key="orr")
        r1,r2=st.columns(2)
        with r1:
            if st.button("Confirm Override",type="primary",use_container_width=True,disabled=not reason.strip(),key="bco"):
                st.session_state.pipeline_status="complete"; st.session_state.show_override_reason_input=False
                ts=datetime.now().strftime("%H:%M:%S")
                st.session_state.agent_messages.append({"stage":"system","time":ts,"sender_name":"System","text":f"🚫 OVERRIDDEN by {on} at {ts} — \"{reason}\"."})
                st.rerun()
        with r2:
            if st.button("Cancel",use_container_width=True): st.session_state.show_override_reason_input=False; st.rerun()

# ── SIDEBAR ────────────────────────────────────────────────────
uh=os.getenv("BAND_USER_HANDLE","").strip().lstrip("@") or "Loan Officer"
ui=uh[0].upper()

with st.sidebar:
    st.html(f"""<div class="sidebar-header">
      <div class="sidebar-logo-icon">🦈</div>
      <div>
        <div class="sidebar-logo-title">LoanShark</div>
        <div class="sidebar-logo-sub">Financial Services</div>
      </div>
    </div>""")

    pages=["⊞  Overview","💳  Applications","🤖  Pipeline Monitor","📋  Audit Logs","⚙️  Settings"]
    sel=st.radio("nav",pages,index=pages.index(st.session_state.current_page) if st.session_state.current_page in pages else 1,label_visibility="collapsed")
    if sel!=st.session_state.current_page: st.session_state.current_page=sel; st.rerun()

    st.html('<div class="sidebar-divider"></div>')
    st.toggle("🛡️ Demo Safe Mode",key="demo_safe_mode")
    st.html('<div class="sidebar-hint">Simulated responses — no live Band API.</div>')

    _s=st.session_state.pipeline_status
    _dm={"running":("run","Running"),"awaiting_approval":("wait","Awaiting Sign-off"),"complete":("done","Complete"),"idle":("idle","Idle")}.get(_s,("idle",_s.title()))
    st.html(f"""<div class="sidebar-status-box">
      <div class="sdot {_dm[0]}"></div>
      <span class="sidebar-status-label">{_dm[1]}</span>
    </div>""")

    st.html(f"""<div class="sidebar-profile">
      <div class="sidebar-avatar">{ui}</div>
      <div>
        <div class="sidebar-user-name">{uh.replace("_"," ").title()}</div>
        <div class="sidebar-user-role">Loan Officer · Admin</div>
      </div>
    </div>""")

# ── SHARED ─────────────────────────────────────────────────────
def topbar(title,sub=""):
    st.html(f"""<div class="topbar">
      <div><h1 class="page-title">{title}</h1><p class="page-sub">{sub or datetime.now().strftime("%B %d, %Y  ·  %H:%M")}</p></div>
      <div style="display:flex;align-items:center;gap:.7rem;">
        <div style="position:relative;width:30px;height:30px;background:var(--canvas);border:1px solid var(--hairline);border-radius:var(--r-btn);display:flex;align-items:center;justify-content:center;font-size:.85rem;cursor:pointer;box-shadow:var(--shadow-sm);">🔔
          <div style="position:absolute;top:-2px;right:-2px;width:7px;height:7px;background:var(--red);border-radius:50%;border:1.5px solid var(--canvas);"></div>
        </div>
        <div style="background:var(--canvas);border:1px solid var(--hairline);border-radius:var(--r-btn);padding:.32rem .85rem;font-size:.76rem;color:var(--ink3);display:flex;align-items:center;gap:.35rem;box-shadow:var(--shadow-sm);min-width:145px;">🔍 Search…</div>
      </div>
    </div>""")

def stepper(msgs):
    reached={m.get("stage") for m in msgs}; err="error" in reached
    order=[s["k"] for s in STAGES]; prog=sum(1 for s in order if s in reached)
    items=[]
    for i,s in enumerate(STAGES):
        cls="done" if s["k"] in reached else ("active" if i==prog and not err else "")
        inner="✓" if cls=="done" else str(i+1)
        items.append(f'<div class="step"><div class="dot {cls}">{inner}</div><div class="slabel {cls}">{s["l"]}</div></div>')
        if i<len(STAGES)-1: items.append(f'<div class="conn {"done" if i<prog else ""}"></div>')
    pct=int(prog/len(STAGES)*100)
    st.html(f"""<div class="card" style="padding:1.2rem 1.5rem;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.9rem;">
        <p class="eyebrow" style="margin:0;">9-Agent AI Pipeline</p>
        <span style="font-size:.75rem;font-weight:600;color:var(--primary);">{prog}/9 stages</span>
      </div>
      <div class="stepper">{"".join(items)}</div>
      <div class="pbar"><div class="pfill" style="width:{pct}%;"></div></div>
    </div>""")

def get_progress(msgs): 
    r={m.get("stage") for m in msgs}
    return sum(1 for s in ["doc","credit","fraud","risk","compliance","decision","pricing","communication","human_gate"] if s in r)

def bam(txt): return txt.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def build_msg(fd):
    return (f"NEW_LOAN_APPLICATION:\nApplicant: {fd['applicant_name']}, Age: {fd['applicant_age']}\n"
            f"Monthly Income: {fd['monthly_income']} {fd['currency']}\n"
            f"Employment: {fd['employment_type']} at {fd.get('employer_name','N/A')} ({fd['years_employed']} years)\n"
            f"Loan: {fd['loan_amount_requested']} {fd['currency']} for {fd['loan_tenure_months']} months, purpose: {fd['loan_purpose']}\n"
            f"Existing Debt: {fd['existing_debt_monthly']} {fd['currency']}\n"
            f"Credit Score: {fd.get('credit_score','Not provided')}\nCollateral: {fd.get('collateral_offered','None')}\n\nPlease process.")

# ── PAGES ──────────────────────────────────────────────────────

def page_applications():
    topbar("New Application","Submit applicant details and launch the AI pipeline")
    dm=st.session_state.get("demo_safe_mode",True); act=st.session_state.active_demo

    st.html('<p class="eyebrow">Quick Demo Scenarios</p>')
    d1,d2,d3=st.columns(3)
    for col,key in[(d1,"good"),(d2,"borderline"),(d3,"highrisk")]:
        s=DEMOS[key]; sel="sel" if act==key else ""
        with col:
            st.html(f"""<div class="sc {sel}">
              <div style="font-size:1rem;margin-bottom:.25rem;">{s['emoji']}</div>
              <div style="font-size:.84rem;font-weight:700;color:var(--ink);">{s['label']}</div>
              <div style="font-size:.71rem;color:var(--ink3);margin:.15rem 0 .5rem;">{s['desc']}</div>
              <span class="badge {s['tc']}">{s['tag']}</span>
            </div>""")
            if st.button("Load",use_container_width=True,key=f"d_{key}"):
                st.session_state.active_demo=key; st.rerun()

    if act:
        d=DEMOS[act]
        st.html(f"""<div style="display:flex;align-items:center;gap:.45rem;padding:.5rem .85rem;background:var(--primary-bg);border:1px solid var(--primary-soft);border-radius:var(--r-btn);margin-bottom:.8rem;font-size:.79rem;color:var(--ink2);">
          {d['emoji']} <strong style="color:var(--ink);">{d['label']}</strong> loaded — review and submit.
        </div>""")

    _d=DEMOS.get(act or "",{})
    with st.form("lf",clear_on_submit=False):
        st.html('<p class="eyebrow">Applicant Information</p>')
        c1,c2,c3=st.columns(3)
        with c1: an=st.text_input("Full Name",value=_d.get("applicant_name",""),placeholder="e.g. Priya Sharma")
        with c2: aa=st.number_input("Age",min_value=18,max_value=70,value=int(_d.get("applicant_age",30)))
        with c3: cur=st.selectbox("Currency",["INR","USD"])
        c4,c5,c6=st.columns(3)
        with c4: cs=st.number_input("CIBIL Score",min_value=0,max_value=900,value=int(_d.get("credit_score") or 0),help="0 = not provided")
        with c5:
            eopts=["salaried","self_employed","business_owner","unemployed"]
            et=st.selectbox("Employment",eopts,index=eopts.index(_d["employment_type"]) if _d.get("employment_type") in eopts else 0)
        with c6: en=st.text_input("Employer / Business",value=_d.get("employer_name") or "",placeholder="Infosys Ltd…")
        c7,c8=st.columns(2)
        with c7: mi=st.number_input("Monthly Income (₹)",min_value=0.,value=float(_d.get("monthly_income",75000.)),step=5000.)
        with c8: ye=st.number_input("Years at Job",min_value=0.,max_value=40.,value=float(_d.get("years_employed",3.)),step=.5)
        st.html('<div style="height:1px;background:var(--hairline);margin:.7rem 0;"></div>')
        st.html('<p class="eyebrow">Loan Details</p>')
        c9,c10,c11=st.columns(3)
        with c9: la=st.number_input("Loan Amount (₹)",min_value=10000.,value=float(_d.get("loan_amount_requested",500000.)),step=10000.)
        with c10:
            lp_opts=["home","vehicle","education","personal","business"]
            lp=st.selectbox("Purpose",lp_opts,index=lp_opts.index(_d["loan_purpose"]) if _d.get("loan_purpose") in lp_opts else 0)
        with c11: ed=st.number_input("Existing Monthly Debt (₹)",min_value=0.,value=float(_d.get("existing_debt_monthly",0.)),step=1000.)
        c12,c13=st.columns([1,2])
        with c12: lt=st.slider("Tenure (months)",6,360,int(_d.get("loan_tenure_months",60)),step=6)
        with c13: col_=st.text_input("Collateral (optional)",value=_d.get("collateral_offered") or "",placeholder="e.g. Residential property…")
        st.html('<div style="height:1px;background:var(--hairline);margin:.7rem 0;"></div>')
        st.html('<p class="eyebrow">Band Connection</p>')
        if dm:
            st.html("""<div style="padding:.5rem .85rem;background:var(--primary-bg);border:1px solid var(--primary-soft);border-radius:var(--r-btn);font-size:.78rem;color:var(--ink2);margin-bottom:.6rem;">
              🛡️ <strong style="color:var(--ink);">Demo Safe Mode ON</strong> — Band credentials not required.</div>""")
        b1,b2=st.columns(2)
        with b1: bci=st.text_input("Band Chat / Room ID",value=st.session_state.chat_id,placeholder="0fc794a9-…",disabled=dm)
        with b2: ih=st.text_input("Intake Agent Handle",value=st.session_state.intake_handle,placeholder="@username/intakeagent",disabled=dm)
        bk=st.text_input("Band Human API Key",type="password",placeholder="Pre-loaded from .env ✓" if is_configured() else "Enter API Key",disabled=dm)
        sub=st.form_submit_button("🚀  Submit Application",use_container_width=True,type="primary")

    if sub:
        if bk.strip(): os.environ["BAND_HUMAN_API_KEY"]=bk.strip()
        if bci.strip(): os.environ["BAND_CHAT_ID"]=bci.strip()
        if not dm and (not an or not bci.strip() or not ih.strip()): st.error("Fill applicant name, Chat ID, and Agent Handle."); return
        if not dm and not is_configured(): st.error(f"Band not configured — missing: {', '.join(missing_config())}."); return
        fd={"applicant_name":an,"applicant_age":aa,"monthly_income":mi,"currency":cur,"employment_type":et,"employer_name":en or None,
            "years_employed":ye,"loan_amount_requested":la,"loan_purpose":lp,"loan_tenure_months":lt,"existing_debt_monthly":ed,
            "credit_score":cs if cs>0 else None,"collateral_offered":col_ or None}
        aid=f"APP-{str(int(time.time()))[-6:]}"
        st.session_state.update({"application_id":aid,"chat_id":bci.strip(),"intake_handle":ih.strip(),
            "pipeline_status":"running","agent_messages":[],"loan_decision":None,"loan_letter":None,
            "seen_message_ids":set(),"show_override_reason_input":False,"current_page":"🤖  Pipeline Monitor","last_form_data":fd})
        ts=datetime.now().strftime("%H:%M:%S")
        if dm:
            st.session_state.update({"replay_step":0,"replay_scenario":act or "good"})
            st.session_state.agent_messages.append({"stage":"system","time":ts,"sender_name":"System","text":f"Application {aid} submitted (Demo: {(act or 'good').title()})."})
        else:
            st.session_state.poll_since=now_iso()
            st.session_state.agent_messages.append({"stage":"system","time":ts,"sender_name":"System","text":f"Application {aid} submitted. Posting to Band…"})
            try:
                post_message(bci.strip(),f"{ih.strip()} {build_msg(fd)}",mention_handle=ih.strip())
                st.session_state.agent_messages.append({"stage":"system","time":datetime.now().strftime("%H:%M:%S"),"sender_name":"System","text":"📡 Posted to Band. Awaiting agents…"})
            except BandClientError as exc:
                st.session_state.pipeline_status="idle"
                st.session_state.agent_messages.append({"stage":"error","time":ts,"sender_name":"System","text":f"Band error: {exc}"})
                st.error(f"Band error: {exc}"); return
        st.rerun()


def page_pipeline():
    fd=st.session_state.get("last_form_data") or st.session_state.get("loan_decision") or {}
    aid=st.session_state.get("application_id","—"); status=st.session_state.pipeline_status; msgs=st.session_state.agent_messages
    sm={"idle":("idle","Idle"),"running":("run","Processing"),"awaiting_approval":("wait","Awaiting Sign-off"),"complete":("done","Completed")}
    dc,sl=sm.get(status,("idle","—"))
    topbar("Pipeline Monitor",f"Application {aid} · {sl}")
    name=fd.get("applicant_name","—"); emp=(fd.get("employment_type") or "—").replace("_"," ").title()
    amt=fmt(fd.get("loan_amount_requested",0)) if fd else "—"; pur=(fd.get("loan_purpose") or "—").title()
    cibil=str(fd.get("credit_score") or "N/A")
    st.html(f"""<div class="card"><p class="eyebrow">Active Application</p>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1.3rem;">
        <div><p style="font-size:.65rem;font-weight:700;color:var(--ink3);text-transform:uppercase;letter-spacing:.08em;margin:0 0 .25rem;">Applicant</p><p style="font-size:.93rem;font-weight:600;color:var(--ink);margin:0;">{name}</p></div>
        <div><p style="font-size:.65rem;font-weight:700;color:var(--ink3);text-transform:uppercase;letter-spacing:.08em;margin:0 0 .25rem;">Employment</p><p style="font-size:.93rem;font-weight:600;color:var(--ink);margin:0;">{emp}</p></div>
        <div><p style="font-size:.65rem;font-weight:700;color:var(--ink3);text-transform:uppercase;letter-spacing:.08em;margin:0 0 .25rem;">Loan Amount</p><p style="font-size:.93rem;font-weight:600;color:var(--ink);margin:0;font-variant-numeric:tabular-nums;">{amt}</p></div>
        <div><p style="font-size:.65rem;font-weight:700;color:var(--ink3);text-transform:uppercase;letter-spacing:.08em;margin:0 0 .25rem;">Purpose</p><p style="font-size:.93rem;font-weight:600;color:var(--ink);margin:0;">{pur}</p></div>
        <div><p style="font-size:.65rem;font-weight:700;color:var(--ink3);text-transform:uppercase;letter-spacing:.08em;margin:0 0 .25rem;">CIBIL Score</p><p style="font-size:.93rem;font-weight:600;color:var(--ink);margin:0;">{cibil}</p></div>
        <div><p style="font-size:.65rem;font-weight:700;color:var(--ink3);text-transform:uppercase;letter-spacing:.08em;margin:0 0 .25rem;">Status</p>
          <span class="spill"><span class="sdot {dc}"></span>{sl}</span></div>
      </div></div>""")

    stepper(msgs)

    am={"doc":"Intake","credit":"Doc Verify","fraud":"Credit","risk":"Fraud","compliance":"Risk","decision":"Compliance","pricing":"Decision","communication":"Pricing","human_gate":"Human Gate","system":"System","thought":"Thinking","error":"Error"}
    if not msgs:
        st.html("""<div class="card" style="text-align:center;padding:2.5rem;">
          <div style="font-size:1.8rem;margin-bottom:.5rem;">🤖</div>
          <div style="font-size:.88rem;font-weight:600;color:var(--ink);">No pipeline active</div>
          <div style="font-size:.76rem;color:var(--ink3);margin-top:.2rem;">Submit an application to start.</div></div>""")
    else:
        sm2={"error":"red","human_gate":"pri","system":"dim","thought":"dim"}
        rows="".join(f'<tr><td class="dim mono">{m.get("time","")}</td><td class="{sm2.get(m.get("stage",""),"teal")}">{"Err" if m.get("stage")=="error" else "Gate" if m.get("stage")=="human_gate" else "Info" if m.get("stage") in("system","thought") else "Done"}</td><td class="b">{bam(m.get("sender_name","Agent"))}</td><td class="dim">{am.get(m.get("stage",""),"—")}</td><td class="b" style="max-width:280px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{bam(([l.strip() for l in m.get("text","").split("\n") if l.strip() and not l.strip().startswith("@")] or [""])[0][:75])}</td></tr>' for m in reversed(msgs))
        st.html(f"""<div class="card"><p class="eyebrow">Agent Log</p>
          <div style="overflow-x:auto;"><table class="tbl">
            <thead><tr><th>Time</th><th>Status</th><th>Agent</th><th>Stage</th><th>Preview</th></tr></thead>
            <tbody>{rows}</tbody></table></div></div>""")

    poll()
    if status=="running":
        with st.expander("📥 Manual Fallback — paste agent message"):
            ar=st.text_area("Paste:",height=80,key="ap")
            if st.button("Process",use_container_width=True): ingest(ar); st.rerun()
    if status=="awaiting_approval" and st.session_state.loan_letter: human_gate()
    audit_panel(msgs,st.session_state.loan_decision,aid)
    if status=="complete":
        st.html("""<div style="padding:.8rem 1.1rem;background:var(--teal-bg);border:1px solid var(--teal-b);border-radius:var(--r-card);font-size:.82rem;color:var(--teal);font-weight:600;margin:1rem 0;">🎉 Application finalized. Audit trail logged.</div>""")
        if st.button("➕ New Application",type="primary",use_container_width=True):
            st.session_state.update({"pipeline_status":"idle","agent_messages":[],"loan_decision":None,"loan_letter":None,"application_id":None,"active_demo":None,"last_form_data":None,"current_page":"💳  Applications"}); st.rerun()


def page_overview():
    topbar("Dashboard","Loan Shark Financial Services · AI Pipeline Overview")
    msgs=st.session_state.agent_messages; status=st.session_state.pipeline_status; aid=st.session_state.application_id
    prog=get_progress(msgs); pct=int(prog/9*100)
    band_ok=is_configured(); demo=st.session_state.get("demo_safe_mode",True)
    appr=any(m.get("stage")=="pricing" for m in msgs)
    st.html(f"""<div class="stat-grid">
      <div class="stat-card"><div class="stat-bar" style="background:var(--primary);"></div><p class="stat-label">Applications</p><p class="stat-val">{1 if aid else 0}</p><p class="stat-sub">{"Active" if aid else "None"}</p></div>
      <div class="stat-card"><div class="stat-bar" style="background:var(--teal);"></div><p class="stat-label">Agents Online</p><p class="stat-val">9</p><p class="stat-sub">LangGraph + Band</p></div>
      <div class="stat-card"><div class="stat-bar" style="background:var(--amber);"></div><p class="stat-label">Pipeline Progress</p><p class="stat-val">{prog}<span style="font-size:.9rem;color:var(--ink3);font-weight:400;">/9</span></p><p class="stat-sub">{pct}%</p></div>
      <div class="stat-card"><div class="stat-bar" style="background:{"var(--teal)" if appr else "var(--ink3)"};"></div><p class="stat-label">Decision</p><p class="stat-val" style="font-size:1.3rem;">{"Issued" if appr else "Pending"}</p><p class="stat-sub">{"Decision reached" if appr else "Awaiting"}</p></div>
    </div>""")
    st.html(f"""<div class="card"><p class="eyebrow">System Health</p>
      <div class="cr"><div><div class="crk">Band API</div><div class="crd">Agent message transport</div></div><span class="badge {"badge-teal" if band_ok else "badge-amber"}">{"Connected" if band_ok else "Demo Mode"}</span></div>
      <div class="cr"><div><div class="crk">Demo Safe Mode</div><div class="crd">Canned responses</div></div><span class="badge {"badge-blue" if demo else "badge-gray"}">{"On" if demo else "Off"}</span></div>
      <div class="cr"><div><div class="crk">Pipeline</div><div class="crd">Current state</div></div><span class="badge {"badge-teal" if status=="complete" else "badge-blue" if status=="awaiting_approval" else "badge-amber" if status=="running" else "badge-gray"}">{status.replace("_"," ").title()}</span></div>
      <div class="cr"><div><div class="crk">Groq LLM</div><div class="crd">llama-3.3-70b-versatile</div></div><span class="badge badge-teal">Active</span></div>
    </div>""")
    if msgs:
        rows="".join(f'<tr><td class="dim mono">{m.get("time","")}</td><td class="{"teal" if m.get("stage") not in("error","system","thought") else "red" if m.get("stage")=="error" else "dim"}">{("Done" if m.get("stage") not in("error","system","thought") else "Err" if m.get("stage")=="error" else "Info")}</td><td class="b">{bam(m.get("sender_name","?"))}</td><td style="max-width:360px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--ink2);">{bam(m.get("text","")[:90])}{"…" if len(m.get("text",""))>90 else ""}</td></tr>' for m in reversed(msgs[-12:]))
        st.html(f"""<div class="card"><p class="eyebrow">Recent Activity</p>
          <div style="overflow-x:auto;"><table class="tbl"><thead><tr><th>Time</th><th>Status</th><th>Agent</th><th>Activity</th></tr></thead><tbody>{rows}</tbody></table></div></div>""")
    else:
        st.html("""<div class="card" style="text-align:center;padding:3rem;">
          <div style="font-size:2.2rem;margin-bottom:.6rem;">🦈</div>
          <div style="font-size:.88rem;font-weight:600;color:var(--ink);">No Activity Yet</div>
          <div style="font-size:.76rem;color:var(--ink3);margin-top:.25rem;">Submit an application to start the pipeline.</div></div>""")


def page_audit():
    topbar("Audit Logs","Immutable compliance record · Band room message history")
    msgs=st.session_state.agent_messages; dec=st.session_state.loan_decision; aid=st.session_state.application_id
    if not msgs:
        st.html("""<div class="card" style="text-align:center;padding:3rem;">
          <div style="font-size:1.8rem;margin-bottom:.6rem;">📋</div>
          <div style="font-size:.88rem;font-weight:600;color:var(--ink);">No Audit Records</div>
          <div style="font-size:.76rem;color:var(--ink3);margin-top:.25rem;">Complete a pipeline run to generate logs.</div></div>"""); return
    rec=(dec or {}).get("recommendation","Pending")
    bc={"APPROVE":"badge-teal","DENY":"badge-red","COUNTER_OFFER":"badge-amber"}.get(rec,"badge-gray")
    st.html(f"""<div class="card"><p class="eyebrow">Application Summary</p>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1.3rem;">
        <div><p style="font-size:.65rem;font-weight:700;color:var(--ink3);text-transform:uppercase;letter-spacing:.08em;margin:0 0 .25rem;">Application ID</p><p style="font-size:.93rem;font-weight:600;color:var(--ink);margin:0;">{aid or "—"}</p></div>
        <div><p style="font-size:.65rem;font-weight:700;color:var(--ink3);text-transform:uppercase;letter-spacing:.08em;margin:0 0 .25rem;">AI Recommendation</p><p style="margin:0;"><span class="badge {bc}">{rec}</span></p></div>
        <div><p style="font-size:.65rem;font-weight:700;color:var(--ink3);text-transform:uppercase;letter-spacing:.08em;margin:0 0 .25rem;">Risk Category</p><p style="font-size:.93rem;font-weight:600;color:var(--ink);margin:0;">{(dec or {}).get("risk_category","—")}</p></div>
        <div><p style="font-size:.65rem;font-weight:700;color:var(--ink3);text-transform:uppercase;letter-spacing:.08em;margin:0 0 .25rem;">Confidence</p><p style="font-size:.93rem;font-weight:600;color:var(--ink);margin:0;">{(dec or {}).get("confidence","—")}</p></div>
        <div><p style="font-size:.65rem;font-weight:700;color:var(--ink3);text-transform:uppercase;letter-spacing:.08em;margin:0 0 .25rem;">Entries Logged</p><p style="font-size:.93rem;font-weight:600;color:var(--ink);margin:0;">{len(msgs)}</p></div>
        <div><p style="font-size:.65rem;font-weight:700;color:var(--ink3);text-transform:uppercase;letter-spacing:.08em;margin:0 0 .25rem;">Generated</p><p style="font-size:.93rem;font-weight:600;color:var(--ink);margin:0;">{datetime.now().strftime("%H:%M, %b %d")}</p></div>
      </div></div>""")
    sb={"doc":"badge-teal","credit":"badge-blue","fraud":"badge-blue","risk":"badge-amber","compliance":"badge-amber","decision":"badge-teal","pricing":"badge-teal","communication":"badge-blue","human_gate":"badge-blue","error":"badge-red","thought":"badge-gray","system":"badge-gray"}
    sn={"doc":"Intake","credit":"Doc Verify","fraud":"Credit","risk":"Fraud","compliance":"Risk","decision":"Compliance","pricing":"Decision","communication":"Pricing","human_gate":"Letter","error":"Error","thought":"Thought","system":"System"}
    rows="".join(f'<tr><td class="dim mono">{m.get("time","")}</td><td><span class="badge {sb.get(m.get("stage","system"),"badge-gray")}">{sn.get(m.get("stage","system"),m.get("stage","").title())}</span></td><td class="b">{bam(m.get("sender_name","?"))}</td><td style="max-width:320px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--ink2);">{bam(m.get("text","")[:90])}{"…" if len(m.get("text",""))>90 else ""}</td></tr>' for m in msgs)
    st.html(f"""<div class="card"><p class="eyebrow">Log — {len(msgs)} entries</p>
      <div style="overflow-x:auto;"><table class="tbl"><thead><tr><th>Time</th><th>Stage</th><th>Agent</th><th>Preview</th></tr></thead><tbody>{rows}</tbody></table></div></div>""")
    c1,c2=st.columns(2)
    with c1: st.download_button("📥 JSON Audit",aj(msgs,dec,aid),f"audit_{aid or 'loan'}.json","application/json",use_container_width=True)
    with c2:
        try: st.download_button("📥 PDF Audit",apdf(msgs,dec,aid),f"audit_{aid or 'loan'}.pdf","application/pdf",use_container_width=True)
        except Exception as e: st.button("📥 PDF (install reportlab)",disabled=True,help=str(e),use_container_width=True)


def page_settings():
    topbar("Settings","System configuration and Band API status")
    band_ok=is_configured(); miss=missing_config(); demo=st.session_state.get("demo_safe_mode",True)
    cid=os.getenv("BAND_CHAT_ID","—"); bu=os.getenv("BAND_REST_URL","https://app.band.ai/")
    gk=os.getenv("GROQ_API_KEY",""); gm=os.getenv("GROQ_MODEL","llama-3.3-70b-versatile")
    uhv=os.getenv("BAND_USER_HANDLE","—"); ae=os.getenv("APP_ENV","development")
    gm_=( gk[:8]+"•••"+gk[-4:]) if len(gk)>12 else ("Set" if gk else "Not set")
    cm_=(cid[:8]+"…"+cid[-4:]) if len(cid)>16 else cid
    st.html(f"""<div class="stat-grid" style="grid-template-columns:repeat(3,1fr);">
      <div class="stat-card"><div class="stat-bar" style="background:{"var(--teal)" if band_ok else "var(--red)"};"></div><p class="stat-label">Band API</p><p class="stat-val" style="font-size:1.25rem;">{"✓ Live" if band_ok else "✗ Off"}</p><p class="stat-sub">{"All creds present" if band_ok else ", ".join(miss)+" missing"}</p></div>
      <div class="stat-card"><div class="stat-bar" style="background:{"var(--teal)" if gk else "var(--red)"};"></div><p class="stat-label">Groq LLM</p><p class="stat-val" style="font-size:1.25rem;">{"✓ Key" if gk else "✗ Off"}</p><p class="stat-sub">{"Key in .env" if gk else "Not set"}</p></div>
      <div class="stat-card"><div class="stat-bar" style="background:{"var(--primary)" if demo else "var(--amber)"};"></div><p class="stat-label">Run Mode</p><p class="stat-val" style="font-size:1.25rem;">{"Demo" if demo else "Live"}</p><p class="stat-sub">{"Safe mode on" if demo else "Band active"}</p></div>
    </div>""")
    st.html(f"""<div class="card"><p class="eyebrow">Band Platform</p>
      <div class="cr"><div><div class="crk">REST URL</div><div class="crd">API base</div></div><div class="crv">{bu}</div></div>
      <div class="cr"><div><div class="crk">Chat / Room ID</div><div class="crd">LoanShark agent room</div></div><div class="crv">{cm_}</div></div>
      <div class="cr"><div><div class="crk">User Handle</div><div class="crd">@mention prefix</div></div><div class="crv">@{uhv}</div></div>
      <div class="cr"><div><div class="crk">Human API Key</div><div class="crd">Posts kickoff messages</div></div><span class="badge {"badge-teal" if band_ok else "badge-red"}">{"Configured" if band_ok else "Missing"}</span></div>
    </div>""")
    st.html(f"""<div class="card"><p class="eyebrow">LLM & Agent Config</p>
      <div class="cr"><div><div class="crk">Groq API Key</div><div class="crd">All 9 agents use this</div></div><div class="crv">{gm_}</div></div>
      <div class="cr"><div><div class="crk">Model</div><div class="crd">LangGraph LLM</div></div><div class="crv">{gm}</div></div>
      <div class="cr"><div><div class="crk">Environment</div><div class="crd">Runtime tier</div></div><span class="badge {"badge-amber" if ae=="development" else "badge-teal"}">{ae.title()}</span></div>
      <div class="cr"><div><div class="crk">Orchestration</div><div class="crd"><code>uv run python run_all.py</code></div></div><div class="crv">LangGraph + Band SDK</div></div>
    </div>""")
    pfx=f"@{uhv}/" if uhv!="—" else "@username/"
    ai=[("IntakeAgent","LOAN_APPLICATION:","Validates raw form input"),("DocumentAgent","DOC_VERIFICATION:","Document checks"),("CreditAgent","CREDIT_ANALYSIS:","CIBIL & credit history"),("FraudAgent","FRAUD_REPORT:","Anomaly detection"),("RiskAgent","RISK_ASSESSMENT:","Composite risk rating"),("ComplianceAgent","COMPLIANCE_CHECK:","RBI regulation checks"),("DecisionAgent","LOAN_DECISION_READY:","APPROVE/DENY/COUNTER"),("PricingAgent","PRICING_TERMS:","EMI & final terms"),("CommunicationAgent","FORMAL_LETTER_READY:","Sanction letter draft")]
    rows="".join(f'<tr><td class="dim">{i+1}</td><td class="b">{n}</td><td class="dim mono">{pfx}{n.lower()}</td><td class="pri mono">{t}</td><td class="dim">{d}</td></tr>' for i,(n,t,d) in enumerate(ai))
    st.html(f"""<div class="card"><p class="eyebrow">9-Agent Pipeline</p>
      <div style="overflow-x:auto;"><table class="tbl"><thead><tr><th>#</th><th>Agent</th><th>Handle</th><th>Output Tag</th><th>Role</th></tr></thead><tbody>{rows}</tbody></table></div></div>""")
    if miss:
        st.html(f'<div style="padding:.65rem .9rem;background:var(--amber-bg);border:1px solid var(--amber-b);border-radius:var(--r-btn);font-size:.78rem;color:var(--amber);">⚠ Missing: <code>{", ".join(miss)}</code> — set in <code>.env</code> to enable live mode.</div>')
    else:
        st.html('<div style="padding:.65rem .9rem;background:var(--teal-bg);border:1px solid var(--teal-b);border-radius:var(--r-btn);font-size:.78rem;color:var(--teal);">✓ All credentials configured. Toggle off Demo Safe Mode in the sidebar to go live.</div>')

# ── ROUTER ─────────────────────────────────────────────────────
p=st.session_state.current_page
if   p=="💳  Applications":    page_applications()
elif p=="🤖  Pipeline Monitor": page_pipeline()
elif p=="⊞  Overview":          page_overview()
elif p=="📋  Audit Logs":       page_audit()
elif p=="⚙️  Settings":         page_settings()
else:                            page_applications()

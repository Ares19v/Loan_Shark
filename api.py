"""
Loan Shark — FastAPI Backend
Serves REST API for the React frontend.
Wraps Band SDK, manages pipeline state, drives the agent pipeline.
"""

import os
import time
from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
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

app = FastAPI(title="LoanShark API")

allowed_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
]
env_origins = os.getenv("CORS_ALLOWED_ORIGINS")
if env_origins:
    allowed_origins.extend([o.strip() for o in env_origins.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if not env_origins else allowed_origins,
    allow_credentials=False if not env_origins else True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# IN-MEMORY STATE  (single-user demo)
# ─────────────────────────────────────────────

state: dict[str, Any] = {
    "pipeline_status": "idle",          # idle | running | awaiting_approval | complete
    "agent_messages": [],
    "loan_decision": None,
    "loan_letter": None,
    "application_id": None,
    "last_form_data": None,
    "chat_id": os.getenv("BAND_CHAT_ID", ""),
    "intake_handle": "",
    "poll_since": None,
    "seen_message_ids": set(),
    "demo_safe_mode": True,
    "replay_step": 0,
    "replay_scenario": "good",
}

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

def fmt_currency(amount, currency="INR"):
    if not amount:
        return "—"
    if currency == "INR":
        return f"₹{float(amount):,.0f}"
    return f"${float(amount):,.0f}"


def detect_stage(text: str) -> str:
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


def ingest_message(msg_or_content) -> bool:
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

    stage = detect_stage(content)
    if msg_type == "thought":
        stage = "thought"
    elif msg_type == "error":
        stage = "error"

    if stage == "system" and sender_type == "User":
        return False

    data = extract_json_from_message(content)

    if stage == "pricing" and data:
        state["loan_decision"] = data
    if stage == "communication" and data and state["loan_decision"]:
        state["loan_decision"] = {**state["loan_decision"], **data}
    if stage == "human_gate" and data:
        state["loan_letter"] = data
        state["pipeline_status"] = "awaiting_approval"

    state["agent_messages"].append({
        "stage": stage,
        "sender_name": sender_name,
        "time": datetime.now().strftime("%H:%M:%S"),
        "text": content,
    })
    return True


def build_application_message(fd: dict) -> str:
    return f"""NEW_LOAN_APPLICATION:
Applicant: {fd['applicant_name']}, Age: {fd['applicant_age']}
Monthly Income: {fd['monthly_income']} {fd['currency']}
Employment: {fd['employment_type']} at {fd.get('employer_name', 'N/A')} ({fd['years_employed']} years)
Loan Request: {fd['loan_amount_requested']} {fd['currency']} for {fd['loan_tenure_months']} months
Purpose: {fd['loan_purpose']}
Existing Monthly Debt: {fd['existing_debt_monthly']} {fd['currency']}
Credit Score: {fd.get('credit_score', 'Not provided')}
Collateral: {fd.get('collateral_offered', 'None')}

Please process this application through the pipeline."""


# ─────────────────────────────────────────────
# REQUEST / RESPONSE MODELS
# ─────────────────────────────────────────────

class ApplicationForm(BaseModel):
    applicant_name: str
    applicant_age: int
    monthly_income: float
    currency: str = "INR"
    employment_type: str
    employer_name: str | None = None
    years_employed: float = 0.0
    loan_amount_requested: float
    loan_purpose: str
    loan_tenure_months: int
    existing_debt_monthly: float = 0.0
    credit_score: int | None = None
    collateral_offered: str | None = None
    band_chat_id: str = ""
    intake_handle: str = ""
    band_human_key: str = ""
    demo_safe_mode: bool = True
    demo_scenario: str | None = None


class OfficerAction(BaseModel):
    action: str          # "approve" | "reject"
    officer_name: str
    override_reason: str | None = None
    adjusted_amount: float | None = None
    adjusted_tenure: int | None = None


# ─────────────────────────────────────────────
# API ROUTES
# ─────────────────────────────────────────────

@app.get("/api/state")
def get_state():
    """Return current pipeline state to the frontend."""
    fd = state["last_form_data"] or {}
    return {
        "pipeline_status": state["pipeline_status"],
        "application_id": state["application_id"],
        "agent_messages": state["agent_messages"],
        "loan_decision": state["loan_decision"],
        "loan_letter": state["loan_letter"],
        "demo_safe_mode": state["demo_safe_mode"],
        "applicant": {
            "name": fd.get("applicant_name", "—"),
            "employment_type": (fd.get("employment_type") or "—").replace("_", " ").title(),
            "loan_amount": fmt_currency(fd.get("loan_amount_requested", 0), fd.get("currency", "INR")),
            "loan_purpose": (fd.get("loan_purpose") or "—").title(),
            "currency": fd.get("currency", "INR"),
        },
    }


@app.get("/api/demos")
def get_demos():
    return {k: {"label": v["label"]} for k, v in DEMO_SCENARIOS.items()}


@app.get("/api/demo/{scenario}")
def get_demo_scenario(scenario: str):
    if scenario not in DEMO_SCENARIOS:
        raise HTTPException(404, f"Scenario '{scenario}' not found")
    return DEMO_SCENARIOS[scenario]


@app.post("/api/application/submit")
def submit_application(form: ApplicationForm):
    if form.band_human_key.strip():
        os.environ["BAND_HUMAN_API_KEY"] = form.band_human_key.strip()
    if form.band_chat_id.strip():
        os.environ["BAND_CHAT_ID"] = form.band_chat_id.strip()

    if not form.demo_safe_mode:
        if not form.applicant_name or not form.band_chat_id.strip() or not form.intake_handle.strip():
            raise HTTPException(400, "Missing applicant name, Band Chat ID, or Intake Handle")
        if not is_configured():
            raise HTTPException(400, f"Band not configured — missing: {', '.join(missing_config())}")

    form_data = {
        "applicant_name": form.applicant_name,
        "applicant_age": form.applicant_age,
        "monthly_income": form.monthly_income,
        "currency": form.currency,
        "employment_type": form.employment_type,
        "employer_name": form.employer_name,
        "years_employed": form.years_employed,
        "loan_amount_requested": form.loan_amount_requested,
        "loan_purpose": form.loan_purpose,
        "loan_tenure_months": form.loan_tenure_months,
        "existing_debt_monthly": form.existing_debt_monthly,
        "credit_score": form.credit_score,
        "collateral_offered": form.collateral_offered,
    }

    app_id = f"APP-{str(int(time.time()))[-6:]}"
    state.update({
        "application_id": app_id,
        "last_form_data": form_data,
        "chat_id": form.band_chat_id.strip(),
        "intake_handle": form.intake_handle.strip(),
        "pipeline_status": "running",
        "agent_messages": [],
        "loan_decision": None,
        "loan_letter": None,
        "seen_message_ids": set(),
        "demo_safe_mode": form.demo_safe_mode,
    })

    if form.demo_safe_mode:
        scenario = form.demo_scenario or "good"
        state["replay_step"] = 0
        state["replay_scenario"] = scenario
        state["agent_messages"].append({
            "stage": "system",
            "sender_name": "System",
            "time": datetime.now().strftime("%H:%M:%S"),
            "text": f"✅ Simulated Application {app_id} submitted. Running Demo-safe Mode ({scenario})...",
        })
    else:
        state["poll_since"] = now_iso()
        state["agent_messages"].append({
            "stage": "system",
            "sender_name": "System",
            "time": datetime.now().strftime("%H:%M:%S"),
            "text": f"✅ Application {app_id} submitted. Triggering 9-agent pipeline via Band...",
        })
        content = f"{form.intake_handle.strip()} {build_application_message(form_data)}"
        try:
            post_message(form.band_chat_id.strip(), content, mention_handle=form.intake_handle.strip())
            state["agent_messages"].append({
                "stage": "system",
                "sender_name": "System",
                "time": datetime.now().strftime("%H:%M:%S"),
                "text": "📡 Posted to Band. Agents are processing...",
            })
        except BandClientError as exc:
            state["pipeline_status"] = "idle"
            raise HTTPException(500, f"Could not post to Band: {exc}")

    return {"application_id": app_id, "status": "running"}


@app.post("/api/pipeline/advance")
def advance_demo():
    """Advance one step in the demo replay."""
    if state["pipeline_status"] != "running" or not state["demo_safe_mode"]:
        return {"advanced": False, "reason": "Not in demo mode or not running"}

    from demo_replay import DEMO_REPLAY_DATA
    scenario = state.get("replay_scenario", "good")
    step = state.get("replay_step", 0)
    canned = DEMO_REPLAY_DATA.get(scenario, [])

    if step >= len(canned):
        return {"advanced": False, "reason": "Replay complete"}

    msg = canned[step]
    ingest_message(msg)
    state["replay_step"] = step + 1
    return {"advanced": True, "step": step + 1, "total": len(canned)}


@app.post("/api/pipeline/poll")
def poll_band():
    """Poll Band for new agent messages (live mode)."""
    if state["demo_safe_mode"]:
        return advance_demo()

    if not state["chat_id"] or not is_configured():
        return {"advanced": False, "reason": "Not configured"}

    try:
        messages = poll_messages(state["chat_id"], state["poll_since"])
    except BandClientError as e:
        raise HTTPException(503, f"Band poll failed: {e}")

    messages = sorted(messages, key=lambda m: m.get("inserted_at") or "")
    advanced = False
    for msg in messages:
        ts = msg.get("inserted_at")
        if ts:
            state["poll_since"] = ts
        msg_id = msg.get("id")
        if msg_id is not None:
            if msg_id in state["seen_message_ids"]:
                continue
            state["seen_message_ids"].add(msg_id)
        sender = msg.get("sender") or {}
        sender_type = sender.get("type") if isinstance(sender, dict) else msg.get("sender_type")
        if sender_type == "User":
            continue
        if ingest_message(msg):
            advanced = True

    return {"advanced": advanced, "message_count": len(state["agent_messages"])}


@app.post("/api/pipeline/ingest")
def manual_ingest(payload: dict):
    """Manually ingest an agent message (fallback for when Band polling is unavailable)."""
    text = payload.get("text", "")
    if not text:
        raise HTTPException(400, "No text provided")
    ingest_message(text)
    return {"ok": True}


@app.post("/api/pipeline/officer-action")
def officer_action(action: OfficerAction):
    """Loan officer approves or rejects."""
    if action.action == "approve":
        state["pipeline_status"] = "complete"
        amt = action.adjusted_amount or (state["loan_decision"] or {}).get("approved_amount", 0)
        tenure = action.adjusted_tenure or (state["loan_decision"] or {}).get("approved_tenure_months", 0)
        state["agent_messages"].append({
            "stage": "system",
            "sender_name": "System",
            "time": datetime.now().strftime("%H:%M:%S"),
            "text": f"✅ APPROVED by {action.officer_name} — Amount: {fmt_currency(amt)}, Tenure: {tenure} months.",
        })
    elif action.action == "reject":
        state["pipeline_status"] = "complete"
        reason = action.override_reason or "Officer override"
        state["agent_messages"].append({
            "stage": "system",
            "sender_name": "System",
            "time": datetime.now().strftime("%H:%M:%S"),
            "text": f"🚫 REJECTED/OVERRIDDEN by {action.officer_name} — Reason: {reason}",
        })
    else:
        raise HTTPException(400, "action must be 'approve' or 'reject'")
    return {"status": state["pipeline_status"]}


@app.post("/api/pipeline/reset")
def reset_pipeline():
    state.update({
        "pipeline_status": "idle",
        "agent_messages": [],
        "loan_decision": None,
        "loan_letter": None,
        "application_id": None,
        "last_form_data": None,
        "replay_step": 0,
    })
    return {"ok": True}


@app.get("/api/application/export_pdf")
def export_pdf():
    """Generates and returns the compliance audit PDF."""
    if not state["agent_messages"]:
        raise HTTPException(400, "No data to export")
    
    from generate_pdf import generate_compliance_pdf
    
    try:
        pdf_bytes = generate_compliance_pdf(
            messages=state["agent_messages"],
            decision=state["loan_decision"],
            application_id=state["application_id"]
        )
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=audit_{state['application_id']}.pdf"}
        )
    except Exception as e:
        raise HTTPException(500, f"Failed to generate PDF: {e}")

# ─────────────────────────────────────────────
# SERVE REACT BUILD (production)
# ─────────────────────────────────────────────

import os as _os
_frontend_dist = _os.path.join(_os.path.dirname(__file__), "frontend", "dist")
if _os.path.isdir(_frontend_dist):
    app.mount("/assets", StaticFiles(directory=f"{_frontend_dist}/assets"), name="assets")

    @app.get("/{full_path:path}")
    def serve_react(full_path: str):
        return FileResponse(f"{_frontend_dist}/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)

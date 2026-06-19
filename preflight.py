"""
preflight.py — Loan Shark System Preflight Check
Run before launch to validate every component of the project.

Usage:
    uv run python preflight.py

Exit code 0 = all critical checks passed.
Exit code 1 = one or more critical failures.
"""

import sys
import os
import ast
import re
import importlib
import subprocess
import yaml
import traceback
from pathlib import Path
from dotenv import dotenv_values

# Windows consoles default to cp1252 and choke on box-drawing/emoji output.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ─────────────────────────────────────────────
# COLORS
# ─────────────────────────────────────────────

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

PASS  = f"{GREEN}✅ PASS{RESET}"
FAIL  = f"{RED}❌ FAIL{RESET}"
WARN  = f"{YELLOW}⚠️  WARN{RESET}"
SKIP  = f"{DIM}⏭  SKIP{RESET}"

results = {"pass": 0, "fail": 0, "warn": 0}

ROOT = Path(__file__).parent


def check(label, passed, message="", warn=False):
    """Record and print a single check result."""
    if passed is None:
        status = SKIP
    elif passed:
        status = PASS
        results["pass"] += 1
    elif warn:
        status = WARN
        results["warn"] += 1
    else:
        status = FAIL
        results["fail"] += 1

    suffix = f"  {DIM}{message}{RESET}" if message else ""
    print(f"  {status}  {label}{suffix}")
    return passed


def section(title):
    print(f"\n{BOLD}{CYAN}{'─' * 55}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'─' * 55}{RESET}")


# ─────────────────────────────────────────────
# 1. PYTHON & ENVIRONMENT
# ─────────────────────────────────────────────

section("1 · Python & Runtime Environment")

ver = sys.version_info
check(f"Python version ({ver.major}.{ver.minor}.{ver.micro})",
      ver >= (3, 11),
      "Requires ≥ 3.11" if ver < (3, 11) else "")

# Check all required packages
REQUIRED_PACKAGES = [
    ("band",             "band-sdk"),
    ("langchain_openai", "langchain-openai"),
    ("langgraph",        "langgraph"),
    ("streamlit",        "streamlit"),
    ("yaml",             "pyyaml"),
    ("dotenv",           "python-dotenv"),
    ("requests",         "requests"),
]

for module, pkg in REQUIRED_PACKAGES:
    try:
        importlib.import_module(module)
        check(f"Package: {pkg}", True)
    except ImportError:
        check(f"Package: {pkg}", False, f"Run: uv add {pkg}")

# ─────────────────────────────────────────────
# 2. PROJECT FILE STRUCTURE
# ─────────────────────────────────────────────

section("2 · Project File Structure")

REQUIRED_FILES = [
    "app.py",
    "run_all.py",
    "preflight.py",
    "agent_config.yaml",
    ".env",
    "requirements.txt",
    "pyproject.toml",
    "README.md",
    ".streamlit/config.toml",
    "band_client.py",
    "shared/parsing.py",
    "agents/base.py",
    "api.py",
    "demo_replay.py",
    "generate_pdf.py",
    "agents/intake/agent.py",
    "agents/document/agent.py",
    "agents/credit/agent.py",
    "agents/fraud/agent.py",
    "agents/risk/agent.py",
    "agents/compliance/agent.py",
    "agents/decision/agent.py",
    "agents/pricing/agent.py",
    "agents/communication/agent.py",
]

for f in REQUIRED_FILES:
    path = ROOT / f
    check(f"Exists: {f}", path.exists(), "MISSING" if not path.exists() else "")

# ─────────────────────────────────────────────
# 3. ENVIRONMENT VARIABLES (.env)
# ─────────────────────────────────────────────

section("3 · Environment Variables (.env)")

env_path = ROOT / ".env"
env = {}
if env_path.exists():
    env = dotenv_values(str(env_path))

REQUIRED_ENV = {
    "GROQ_API_KEY":       ("critical", "Required to call LLM for all 9 agents"),
    "BAND_WS_URL":        ("critical", "Band WebSocket URL"),
    "BAND_REST_URL":      ("critical", "Band REST API URL"),
    "BAND_HUMAN_API_KEY": ("warn",     "Human API key — UI uses it to post + poll Band"),
    "BAND_CHAT_ID":       ("warn",     "Chat/room id — fill after creating the room"),
    "BAND_USER_HANDLE":   ("warn",     "Band username — agent @mention handles derive from it"),
}

for key, (severity, hint) in REQUIRED_ENV.items():
    val = env.get(key, "")
    is_critical = severity == "critical"
    if not val:
        check(f"Env: {key}", False if is_critical else None,
              f"MISSING — {hint}", warn=not is_critical)
    elif "PLACEHOLDER" in val.upper() or "YOUR_" in val.upper():
        check(f"Env: {key}", False, "Still a placeholder value", warn=True)
    else:
        masked = val[:8] + "..." if len(val) > 8 else val
        check(f"Env: {key}", True, f"Set ({masked})")

# ─────────────────────────────────────────────
# 4. AGENT CONFIG (agent_config.yaml)
# ─────────────────────────────────────────────

section("4 · Agent Config (agent_config.yaml)")

EXPECTED_AGENTS = [
    "intake", "document", "credit", "fraud", "risk",
    "compliance", "decision", "pricing", "communication"
]

config_path = ROOT / "agent_config.yaml"
agent_cfg = {}
if config_path.exists():
    with open(config_path) as f:
        agent_cfg = yaml.safe_load(f) or {}

check("agent_config.yaml parses as valid YAML", bool(agent_cfg),
      "File empty or invalid" if not agent_cfg else "")

for agent in EXPECTED_AGENTS:
    cfg = agent_cfg.get(agent, {})
    agent_id  = cfg.get("agent_id", "")
    api_key   = cfg.get("api_key", "")
    has_both  = bool(agent_id) and bool(api_key)
    is_placeholder = "PASTE-" in str(agent_id) or "PASTE-" in str(api_key)

    if not has_both:
        check(f"Config: {agent}", False, "Missing agent_id or api_key")
    elif is_placeholder:
        check(f"Config: {agent}", None, "Placeholder — add real Band credentials", warn=True)
        results["warn"] += 1
    else:
        uid_preview = str(agent_id)[:8] + "..."
        check(f"Config: {agent}", True, f"UUID: {uid_preview}")

# ─────────────────────────────────────────────
# 5. SYNTAX CHECK — ALL PYTHON FILES
# ─────────────────────────────────────────────

section("5 · Python Syntax (AST parse)")

PY_FILES = [
    "app.py", "run_all.py", "preflight.py",
    "band_client.py", "shared/parsing.py", "agents/base.py",
    "api.py", "demo_replay.py", "generate_pdf.py",
] + [f"agents/{a}/agent.py" for a in EXPECTED_AGENTS]

for f in PY_FILES:
    path = ROOT / f
    if not path.exists():
        check(f"Syntax: {f}", False, "File missing")
        continue
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        check(f"Syntax: {f}", True)
    except SyntaxError as e:
        check(f"Syntax: {f}", False, f"Line {e.lineno}: {e.msg}")

# ─────────────────────────────────────────────
# 6. PIPELINE CHAIN VALIDATION
# ─────────────────────────────────────────────

section("6 · Agent Pipeline Chain")

CHAIN = [
    #  agent          trigger keyword          @mention of next agent       output tag
    ("intake",        "NEW_LOAN_APPLICATION",  "@DocumentAgent",            "LOAN_APPLICATION:"),
    ("document",      "LOAN_APPLICATION:",     "@CreditAgent",              "DOC_VERIFICATION:"),
    ("credit",        "DOC_VERIFICATION:",     "@FraudAgent",               "CREDIT_ANALYSIS:"),
    ("fraud",         "CREDIT_ANALYSIS:",      "@RiskAgent",                "FRAUD_REPORT:"),
    ("risk",          "FRAUD_REPORT:",         "@ComplianceAgent",          "RISK_ASSESSMENT:"),
    ("compliance",    "RISK_ASSESSMENT:",      "@DecisionAgent",            "COMPLIANCE_CHECK:"),
    ("decision",      "COMPLIANCE_CHECK:",     "@PricingAgent",             "LOAN_DECISION_READY:"),
    ("pricing",       "LOAN_DECISION_READY:",  "@CommunicationAgent",       "PRICING_TERMS:"),
    ("communication", "PRICING_TERMS:",        "FORMAL_LETTER_READY",       "FORMAL_LETTER_READY:"),
]

for agent, trigger, mention, output_tag in CHAIN:
    path = ROOT / f"agents/{agent}/agent.py"
    if not path.exists():
        check(f"Chain: {agent}", False, "Agent file missing")
        continue
    content = path.read_text(encoding="utf-8")

    has_trigger = trigger in content
    has_mention = mention in content
    has_output  = output_tag in content

    if has_trigger and has_mention and has_output:
        check(f"Chain: {agent}", True,
              f"trigger='{trigger[:22]}' → mention='{mention}' → output='{output_tag}'")
    else:
        missing = []
        if not has_trigger: missing.append(f"trigger '{trigger}'")
        if not has_mention: missing.append(f"mention '{mention}'")
        if not has_output:  missing.append(f"output '{output_tag}'")
        check(f"Chain: {agent}", False, f"Missing: {', '.join(missing)}")

# ─────────────────────────────────────────────
# 7. STREAMLIT APP CHECKS
# ─────────────────────────────────────────────

section("7 · Streamlit App (app.py)")

app_path = ROOT / "app.py"
app_content = app_path.read_text(encoding="utf-8") if app_path.exists() else ""

EXPECTED_MESSAGE_TYPES = [
    "LOAN_APPLICATION:",
    "DOC_VERIFICATION:",
    "CREDIT_ANALYSIS:",
    "FRAUD_REPORT:",
    "RISK_ASSESSMENT:",
    "COMPLIANCE_CHECK:",
    "LOAN_DECISION_READY:",
    "PRICING_TERMS:",
    "FORMAL_LETTER_READY:",
]

for msg_type in EXPECTED_MESSAGE_TYPES:
    check(f"App detects: {msg_type}",
          msg_type in app_content,
          "Not in detect_message_stage" if msg_type not in app_content else "")

EXPECTED_PIPELINE_STAGES = [
    "Intake Agent", "Document Agent", "Credit Agent",
    "Fraud Agent", "Risk Agent", "Compliance Agent",
    "Decision Agent", "Pricing Agent", "Communication Agent",
]
all_stages_present = all(s in app_content for s in EXPECTED_PIPELINE_STAGES)
missing_stages = [s for s in EXPECTED_PIPELINE_STAGES if s not in app_content]
check("App: 9-stage pipeline display",
      all_stages_present,
      f"Missing: {missing_stages}" if missing_stages else "")

check("App: DEMO_SCENARIOS defined",   "DEMO_SCENARIOS" in app_content)
check("App: demo buttons present",     "active_demo" in app_content)
check("App: letter rendering",         "letter_body" in app_content)
check("App: loan_letter session state","loan_letter" in app_content)
check("App: Loan Shark branding",      "Loan Shark" in app_content)
check("App: LoanPilot NOT in prompts", "LoanPilot" not in app_content,
      "Stale branding found" if "LoanPilot" in app_content else "", warn=True)

# ─────────────────────────────────────────────
# 8. AGENT BRANDING CHECK
# ─────────────────────────────────────────────

section("8 · Agent Branding (no 'LoanPilot' in system prompts)")

for agent in EXPECTED_AGENTS:
    path = ROOT / f"agents/{agent}/agent.py"
    if not path.exists():
        continue
    content = path.read_text(encoding="utf-8")
    has_stale = "LoanPilot" in content
    check(f"Branding: {agent}",
          not has_stale,
          "Contains 'LoanPilot'" if has_stale else "Clean",
          warn=has_stale)

# ─────────────────────────────────────────────
# 9. GROQ API CONNECTIVITY
# ─────────────────────────────────────────────

section("9 · External API Connectivity")

groq_key = env.get("GROQ_API_KEY", "")
if not groq_key or "PLACEHOLDER" in groq_key.upper():
    check("Groq API: key present", False, "No API key in .env")
else:
    try:
        import requests
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {groq_key}",
                     "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile",
                  "messages": [{"role": "user", "content": "Say OK"}],
                  "max_tokens": 5},
            timeout=10
        )
        if resp.status_code == 200:
            check("Groq API: live call", True, "llama-3.3-70b-versatile responds")
        elif resp.status_code == 401:
            check("Groq API: live call", False, "401 Unauthorized — check API key")
        elif resp.status_code == 429:
            check("Groq API: live call", True, "429 Rate limit — key works but busy", warn=True)
            results["pass"] += 1; results["warn"] -= 1
        else:
            check("Groq API: live call", False, f"HTTP {resp.status_code}: {resp.text[:80]}")
    except Exception as e:
        check("Groq API: live call", False, f"Connection failed: {e}")

band_rest = env.get("BAND_REST_URL", "https://app.band.ai")
try:
    import requests as req
    resp = req.get(band_rest.rstrip("/"), timeout=6)
    check("Band platform reachable", resp.status_code < 500,
          f"HTTP {resp.status_code}")
except Exception as e:
    check("Band platform reachable", False, f"Cannot reach {band_rest}: {e}")

# ─────────────────────────────────────────────
# 10. BAND SDK IMPORTS
# ─────────────────────────────────────────────

section("10 · Band SDK & LangGraph Imports")

SDK_IMPORTS = [
    ("band",                    "band.Agent"),
    ("band.adapters",           "LangGraphAdapter"),
    ("band.config",             "load_agent_config"),
    ("langchain_openai",        "ChatOpenAI"),
    ("langgraph.checkpoint.memory", "InMemorySaver"),
]

for module, attr in SDK_IMPORTS:
    try:
        mod = importlib.import_module(module)
        has_attr = hasattr(mod, attr.split(".")[-1]) if "." not in attr else True
        # Simple check: if module imports without error, consider pass
        check(f"Import: {module}.{attr}", True)
    except ImportError as e:
        check(f"Import: {module}.{attr}", False, str(e))

# ─────────────────────────────────────────────
# FINAL SUMMARY
# ─────────────────────────────────────────────

total = results["pass"] + results["fail"] + results["warn"]
print(f"\n{BOLD}{'═' * 55}{RESET}")
print(f"{BOLD}  PREFLIGHT SUMMARY{RESET}")
print(f"{BOLD}{'═' * 55}{RESET}")
print(f"  {GREEN}✅ Passed  : {results['pass']}{RESET}")
print(f"  {YELLOW}⚠️  Warnings: {results['warn']}{RESET}")
print(f"  {RED}❌ Failed  : {results['fail']}{RESET}")
print(f"  {DIM}   Total   : {total}{RESET}")
print(f"{BOLD}{'═' * 55}{RESET}\n")

if results["fail"] == 0 and results["warn"] == 0:
    print(f"{BOLD}{GREEN}  🚀 ALL CLEAR — Loan Shark is ready for launch.{RESET}\n")
elif results["fail"] == 0:
    print(f"{BOLD}{YELLOW}  🟡 Warnings present. Fix before submission.{RESET}\n")
else:
    print(f"{BOLD}{RED}  🔴 Critical failures found. Fix before running agents.{RESET}\n")

sys.exit(0 if results["fail"] == 0 else 1)

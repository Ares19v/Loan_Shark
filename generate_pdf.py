"""
generate_pdf.py - Loan Shark: Complete Project Documentation
Professional, clean PDF using ReportLab.
Output: Desktop/LoanShark_Documentation.pdf
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)

# ─── PAGE GEOMETRY ────────────────────────────────────────────────────────────
PW, PH = A4          # 595.27 x 841.89 pts
LM = RM = 2 * cm     # 56.69 pts each side
TM = 2.4 * cm        # top margin (reserved for header band)
BM = 1.8 * cm        # bottom margin (reserved for footer)
UW = PW - LM - RM   # usable content width ≈ 481.88 pts

# ─── COLORS ───────────────────────────────────────────────────────────────────
DARK    = HexColor("#0d1b2e")
NAVY    = HexColor("#0f3460")
NAVY2   = HexColor("#16213e")
CYAN    = HexColor("#00BCD4")
CYAN_L  = HexColor("#63b3ed")
GREEN   = HexColor("#4CAF50")
PURPLE  = HexColor("#673AB7")
BODY    = HexColor("#1a202c")
SUBTLE  = HexColor("#718096")
LGREY   = HexColor("#f7fafc")
BGCODE  = HexColor("#e8edf2")
BGTBL   = HexColor("#ebf8ff")
BORDER  = HexColor("#bee3f8")
RED     = HexColor("#c53030")
GOLD    = HexColor("#b7791f")
WHITE   = HexColor("#ffffff")

# ─── OUTPUT ───────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT     = os.path.join(SCRIPT_DIR, "LoanShark_Documentation.pdf")

# ─── PAGE CALLBACKS ───────────────────────────────────────────────────────────
def draw_cover(canvas, doc):
    canvas.saveState()
    # Full dark background
    canvas.setFillColor(DARK)
    canvas.rect(0, 0, PW, PH, fill=1, stroke=0)
    # Top cyan accent strip
    canvas.setFillColor(CYAN)
    canvas.rect(0, PH - 6*mm, PW, 6*mm, fill=1, stroke=0)
    # Bottom navy bar
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, PW, 1.6*cm, fill=1, stroke=0)
    # Footer text
    canvas.setFillColor(HexColor("#a0aec0"))
    canvas.setFont("Helvetica", 8)
    canvas.drawString(2*cm, 0.55*cm,
        "TrenCoders  |  Band of Agents Hackathon 2026  |  "
        "Track 3: Regulated & High-Stakes Workflows")
    canvas.restoreState()

def draw_page(canvas, doc):
    canvas.saveState()
    # Header bar
    canvas.setFillColor(NAVY)
    canvas.rect(0, PH - 1.5*cm, PW, 1.5*cm, fill=1, stroke=0)
    canvas.setFillColor(CYAN)
    canvas.rect(0, PH - 1.5*cm, PW, 2*mm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(2*cm, PH - 1.0*cm, "LOAN SHARK")
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(PW - 2*cm, PH - 1.0*cm,
        "AI-Powered Loan Processing  |  9-Agent Pipeline")
    # Footer bar
    canvas.setFillColor(LGREY)
    canvas.rect(0, 0, PW, 1.3*cm, fill=1, stroke=0)
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(0, 1.3*cm, PW, 1.3*cm)
    canvas.setFillColor(SUBTLE)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(2*cm, 0.48*cm,
        "TrenCoders  |  Band of Agents Hackathon 2026")
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawRightString(PW - 2*cm, 0.48*cm, f"Page {doc.page}")
    canvas.restoreState()

# ─── STYLES ───────────────────────────────────────────────────────────────────
def styles():
    S = {}

    # Cover
    S["cov_title"] = ParagraphStyle("cov_title", fontName="Helvetica-Bold",
        fontSize=36, textColor=WHITE, leading=44, alignment=TA_CENTER, spaceAfter=4)
    S["cov_sub"] = ParagraphStyle("cov_sub", fontName="Helvetica",
        fontSize=15, textColor=CYAN_L, leading=22, alignment=TA_CENTER, spaceAfter=4)
    S["cov_meta"] = ParagraphStyle("cov_meta", fontName="Helvetica",
        fontSize=10, textColor=HexColor("#718096"), leading=16, alignment=TA_CENTER)
    S["cov_team"] = ParagraphStyle("cov_team", fontName="Helvetica-Bold",
        fontSize=13, textColor=GREEN, leading=18, alignment=TA_CENTER, spaceAfter=4)

    # Headings
    S["h1"] = ParagraphStyle("h1", fontName="Helvetica-Bold",
        fontSize=16, textColor=WHITE, leading=22, spaceAfter=4, spaceBefore=4)
    S["h2"] = ParagraphStyle("h2", fontName="Helvetica-Bold",
        fontSize=13, textColor=NAVY, leading=18, spaceAfter=5, spaceBefore=12)
    S["h3"] = ParagraphStyle("h3", fontName="Helvetica-Bold",
        fontSize=11, textColor=CYAN, leading=16, spaceAfter=3, spaceBefore=8)
    S["h4"] = ParagraphStyle("h4", fontName="Helvetica-Bold",
        fontSize=10, textColor=BODY, leading=14, spaceAfter=2, spaceBefore=5)

    # Body
    S["body"] = ParagraphStyle("body", fontName="Helvetica",
        fontSize=10, textColor=BODY, leading=15, spaceAfter=3, spaceBefore=2,
        alignment=TA_JUSTIFY)
    S["body_l"] = ParagraphStyle("body_l", fontName="Helvetica",
        fontSize=10, textColor=BODY, leading=15, spaceAfter=2, spaceBefore=2)
    S["small"] = ParagraphStyle("small", fontName="Helvetica",
        fontSize=8.5, textColor=SUBTLE, leading=12)
    S["bullet"] = ParagraphStyle("bullet", fontName="Helvetica",
        fontSize=10, textColor=BODY, leading=14, spaceAfter=1, spaceBefore=1,
        leftIndent=16, firstLineIndent=-10)

    # Code
    S["code"] = ParagraphStyle("code", fontName="Courier",
        fontSize=8, textColor=HexColor("#1a365d"), leading=12)

    # Table cells
    S["th"] = ParagraphStyle("th", fontName="Helvetica-Bold",
        fontSize=9, textColor=WHITE, leading=13)
    S["td"] = ParagraphStyle("td", fontName="Helvetica",
        fontSize=9, textColor=BODY, leading=13)
    S["td_b"] = ParagraphStyle("td_b", fontName="Helvetica-Bold",
        fontSize=9, textColor=BODY, leading=13)

    # TOC
    S["toc_1"] = ParagraphStyle("toc_1", fontName="Helvetica-Bold",
        fontSize=11, textColor=NAVY, leading=17, spaceBefore=5, spaceAfter=1)
    S["toc_2"] = ParagraphStyle("toc_2", fontName="Helvetica",
        fontSize=10, textColor=BODY, leading=14, spaceBefore=1, leftIndent=22)

    # Misc
    S["center"] = ParagraphStyle("center", fontName="Helvetica",
        fontSize=10, textColor=BODY, leading=14, alignment=TA_CENTER)
    S["caption"] = ParagraphStyle("caption", fontName="Helvetica-Oblique",
        fontSize=8.5, textColor=SUBTLE, leading=12, alignment=TA_CENTER,
        spaceBefore=2, spaceAfter=4)

    return S

# ─── COMPONENT BUILDERS ───────────────────────────────────────────────────────

def HR(thickness=0.5, color=CYAN, sb=6, sa=6):
    return HRFlowable(width="100%", thickness=thickness, color=color,
                      spaceBefore=sb, spaceAfter=sa)

def sec_header(text, S):
    """Dark navy section header box with white text and cyan underline."""
    t = Table([[Paragraph(text, S["h1"])]], colWidths=[UW])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), NAVY),
        ("LEFTPADDING",   (0,0), (-1,-1), 14),
        ("RIGHTPADDING",  (0,0), (-1,-1), 14),
        ("TOPPADDING",    (0,0), (-1,-1), 9),
        ("BOTTOMPADDING", (0,0), (-1,-1), 9),
        ("LINEBELOW",     (0,0), (-1,-1), 3, CYAN),
    ]))
    return t

def agent_box(num, name, trigger, output, S):
    """Styled agent section header."""
    row1 = [Paragraph(
        f'<font color="#00BCD4"><b>Agent {num} of 9</b></font>'
        f'  <font color="#ffffff"> &mdash; {name}</font>', S["h2"])]
    row2 = [Paragraph(
        f'<font color="#63b3ed"><b>Trigger:</b></font> '
        f'<font color="#a0aec0">{trigger}</font>'
        f'&nbsp;&nbsp;&nbsp;&nbsp;'
        f'<font color="#63b3ed"><b>Output:</b></font> '
        f'<font color="#a0aec0">{output}</font>',
        S["small"])]
    t = Table([[row1[0]], [row2[0]]], colWidths=[UW])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), NAVY2),
        ("LEFTPADDING",   (0,0), (-1,-1), 14),
        ("RIGHTPADDING",  (0,0), (-1,-1), 14),
        ("TOPPADDING",    (0,0), (0,0),   10),
        ("BOTTOMPADDING", (0,-1),(-1,-1), 10),
        ("TOPPADDING",    (0,1), (-1,-1), 2),
        ("LINEAFTER",     (0,0), (-1,-1), 3, CYAN),
        ("LINEBELOW",     (0,-1),(-1,-1), 0.5, HexColor("#2d3748")),
    ]))
    return t

def code_block(text, S, label=None):
    """Code block as a styled table cell."""
    items = []
    if label:
        items.append(Paragraph(label, ParagraphStyle("cl",
            fontName="Helvetica-Bold", fontSize=8, textColor=SUBTLE,
            leading=11, spaceBefore=8, spaceAfter=2)))
    lines = text.strip("\n").split("\n")
    # Build single cell with all lines as sub-table
    rows = [[Paragraph(
        ln.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace(" ", "&nbsp;") or "&nbsp;",
        S["code"]
    )] for ln in lines]
    inner = Table(rows, colWidths=[UW - 28])
    inner.setStyle(TableStyle([
        ("LEFTPADDING",  (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING",   (0,0), (-1,-1), 1),
        ("BOTTOMPADDING",(0,0), (-1,-1), 1),
        ("BACKGROUND",   (0,0), (-1,-1), BGCODE),
    ]))
    wrapper = Table([[inner]], colWidths=[UW])
    wrapper.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), BGCODE),
        ("LEFTPADDING",   (0,0), (-1,-1), 14),
        ("RIGHTPADDING",  (0,0), (-1,-1), 10),
        ("TOPPADDING",    (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("BOX",           (0,0), (-1,-1), 0.5, CYAN),
        ("LINEBEFORE",    (0,0), (-1,-1), 3,   NAVY),
    ]))
    items.append(wrapper)
    return items

def data_table(header_row, data_rows, col_widths, S):
    """Professional styled data table."""
    all_rows = [header_row] + data_rows
    t = Table(all_rows, colWidths=col_widths, repeatRows=1)
    ts = [
        # Header
        ("BACKGROUND",    (0,0), (-1,0),  NAVY),
        ("TEXTCOLOR",     (0,0), (-1,0),  WHITE),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,0),  9),
        ("TOPPADDING",    (0,0), (-1,0),  7),
        ("BOTTOMPADDING", (0,0), (-1,0),  7),
        # Data rows
        ("FONTNAME",      (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,1), (-1,-1), 9),
        ("TOPPADDING",    (0,1), (-1,-1), 5),
        ("BOTTOMPADDING", (0,1), (-1,-1), 5),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, BGTBL]),
        # Grid
        ("GRID",          (0,0), (-1,-1), 0.4, BORDER),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        # All padding
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
    ]
    t.setStyle(TableStyle(ts))
    return t

def P(text, s):
    return Paragraph(text, s)

def B(text, S, indent=0):
    """Bullet point."""
    sp = S["bullet"] if indent == 0 else ParagraphStyle("bi2",
        parent=S["bullet"], leftIndent=32, firstLineIndent=-10)
    return Paragraph(f"- {text}", sp)

def SP(h=0.2):
    return Spacer(1, h*cm)

# ─── SECTIONS ─────────────────────────────────────────────────────────────────

def build_cover(S):
    story = []
    # Push content down to vertical center of dark page
    story.append(SP(6.5))
    story.append(P("LOAN SHARK", S["cov_title"]))
    story.append(SP(0.15))
    story.append(P("AI-Powered Loan Processing", S["cov_sub"]))
    story.append(P("9 Agents  |  One Decision  |  Zero Shortcuts", S["cov_sub"]))
    story.append(SP(0.4))
    # Cyan divider
    story.append(HR(1.5, CYAN, 4, 16))
    story.append(P("Band of Agents Hackathon 2026", S["cov_meta"]))
    story.append(P("Track 3: Regulated &amp; High-Stakes Workflows", S["cov_meta"]))
    story.append(SP(0.15))
    story.append(P("Team: TrenCoders", S["cov_team"]))
    story.append(SP(0.8))

    # Stats row
    stat_data = [[
        P('<font color="#00BCD4"><b><font size="22">9</font></b></font><br/>'
          '<font color="#718096">Specialized AI Agents</font>', S["center"]),
        P('<font color="#00BCD4"><b><font size="22">3</font></b></font><br/>'
          '<font color="#718096">Decision Outcomes</font>', S["center"]),
        P('<font color="#00BCD4"><b><font size="22">94</font></b></font><br/>'
          '<font color="#718096">Preflight Checks</font>', S["center"]),
        P('<font color="#00BCD4"><b><font size="22">100%</font></b></font><br/>'
          '<font color="#718096">Human Sign-off</font>', S["center"]),
    ]]
    st = Table(stat_data, colWidths=[UW/4]*4)
    st.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), HexColor("#111827")),
        ("BOX",           (0,0), (-1,-1), 1,   CYAN),
        ("LINEBEFORE",    (1,0), (-1,-1), 0.5, HexColor("#374151")),
        ("TOPPADDING",    (0,0), (-1,-1), 14),
        ("BOTTOMPADDING", (0,0), (-1,-1), 14),
        ("LEFTPADDING",   (0,0), (-1,-1), 4),
        ("RIGHTPADDING",  (0,0), (-1,-1), 4),
    ]))
    story.append(st)
    story.append(SP(0.6))
    story.append(P(
        "This document provides a complete technical reference for Loan Shark — "
        "a 9-agent AI loan processing pipeline built on Band SDK, LangGraph, and Groq.",
        ParagraphStyle("ci", fontName="Helvetica-Oblique", fontSize=10,
                       textColor=HexColor("#9ca3af"), leading=16, alignment=TA_CENTER)))
    return story

def build_toc(S):
    story = [PageBreak()]
    story.append(P("Table of Contents", ParagraphStyle("toch",
        fontName="Helvetica-Bold", fontSize=20, textColor=NAVY,
        leading=26, spaceBefore=10, spaceAfter=10)))
    story.append(HR())

    sections = [
        (True,  "1.  Executive Summary"),
        (True,  "2.  The Problem"),
        (True,  "3.  The Solution"),
        (True,  "4.  System Architecture"),
        (False, "4.1  High-Level Overview"),
        (False, "4.2  Pipeline Architecture"),
        (False, "4.3  Communication Model"),
        (False, "4.4  Data Enrichment Chain"),
        (True,  "5.  The 9-Agent Pipeline"),
        (False, "5.1  Intake Agent"),
        (False, "5.2  Document Verification Agent"),
        (False, "5.3  Credit Analysis Agent"),
        (False, "5.4  Fraud Detection Agent"),
        (False, "5.5  Risk Assessment Agent"),
        (False, "5.6  Compliance Agent"),
        (False, "5.7  Decision Agent"),
        (False, "5.8  Pricing Agent"),
        (False, "5.9  Communication Agent"),
        (True,  "6.  Message Protocol &amp; Data Schema"),
        (False, "6.1  Message Format Specification"),
        (False, "6.2  JSON Payload Schema"),
        (False, "6.3  Full Message Tag Reference"),
        (True,  "7.  Technology Stack"),
        (False, "7.1  Band SDK"),
        (False, "7.2  LangGraph"),
        (False, "7.3  Groq LLM"),
        (False, "7.4  Streamlit Frontend"),
        (False, "7.5  Package Management (uv)"),
        (True,  "8.  Compliance &amp; Regulatory Framework"),
        (False, "8.1  RBI Guidelines Implemented"),
        (False, "8.2  Hard Blocks vs Soft Flags"),
        (False, "8.3  Fair Lending Checks"),
        (True,  "9.  Human-in-the-Loop Design"),
        (True,  "10. Frontend — Streamlit Application"),
        (True,  "11. Setup &amp; Deployment Guide"),
        (True,  "12. Quality Assurance — Preflight Check"),
        (True,  "13. Hackathon Track Alignment"),
        (True,  "14. Future Roadmap"),
        (True,  "Appendix A — Project File Structure"),
        (True,  "Appendix B — Configuration Reference"),
        (True,  "Appendix C — API Message Reference"),
    ]
    for is_top, text in sections:
        style = S["toc_1"] if is_top else S["toc_2"]
        story.append(P(text, style))
    return story

def build_s1(S):
    story = [PageBreak(), sec_header("1.  Executive Summary", S), SP(0.3)]
    story.append(P(
        "Loan Shark is a production-grade, multi-agent AI system that automates the "
        "end-to-end processing of loan applications through a sequential pipeline of "
        "9 specialized AI agents. Built for the Band of Agents Hackathon 2026 "
        "(Track 3: Regulated &amp; High-Stakes Workflows), the system demonstrates how "
        "autonomous agents can handle complex, regulated financial workflows while "
        "maintaining full compliance and mandatory human oversight.", S["body"]))
    story.append(SP(0.2))

    w1, w2 = UW * 0.42, UW * 0.58
    kpi = [
        [P("<b>Metric</b>", S["th"]),         P("<b>Value</b>", S["th"])],
        ["Number of AI Agents",               "9 specialized, independent agents"],
        ["LLM Model",                         "Groq llama-3.3-70b-versatile"],
        ["Agent Runtime",                     "LangGraph + Band SDK"],
        ["Coordination Protocol",             "Band @mention real-time messaging"],
        ["Decision Outcomes",                 "APPROVE / DENY / COUNTER_OFFER"],
        ["Compliance Framework",              "RBI Lending Guidelines (India)"],
        ["Human Oversight",                   "Mandatory at every final decision"],
        ["Audit Trail",                       "Band room conversation history (immutable)"],
        ["Frontend",                          "Streamlit web application"],
        ["System Validation Checks",          "94 preflight assertions across 10 categories"],
        ["Language",                          "Python 3.11+"],
        ["Package Manager",                   "uv (Astral)"],
    ]
    rows = [[P(r[0], S["td_b"]) if isinstance(r[0], str) else r[0],
             P(r[1], S["td"])   if isinstance(r[1], str) else r[1]]
            for r in kpi[1:]]
    story.append(data_table(kpi[0], rows, [w1, w2], S))

    story.append(P("Key Innovation", S["h2"]))
    story.append(P(
        "The system uses Band's real-time messaging as BOTH the coordination layer AND "
        "the compliance audit trail. Every agent handoff, every piece of enriched data, "
        "and every decision flag is recorded in the Band room as an immutable, timestamped "
        "message. This dual-purpose architecture means the legally required audit trail "
        "emerges naturally from the system's operation — no separate logging infrastructure needed.",
        S["body"]))
    return story

def build_s2(S):
    story = [PageBreak(), sec_header("2.  The Problem", S), SP(0.3)]
    story.append(P(
        "The traditional loan processing industry suffers from systemic inefficiencies "
        "that cost financial institutions billions annually and frustrate applicants with "
        "opaque, slow, and inconsistent experiences.", S["body"]))
    story.append(SP(0.2))

    problems = [
        ("Slow Processing Times",
         "3-14 Days",
         "Applications bounce between fraud, credit, compliance, and legal departments — "
         "each with its own queue, tooling, and communication style. Applicants wait. "
         "Interest accrues. Competitors win."),
        ("Data Loss at Handoffs",
         "Critical Risk",
         "When a loan officer passes an application to a fraud analyst to a compliance officer, "
         "context is routinely lost. Notes are informal, context is verbal. By the time a "
         "decision is made, the compliance team is working with an incomplete picture."),
        ("Inconsistent Decision-Making",
         "Regulatory Risk",
         "Different loan officers apply different thresholds. Two identical applications may "
         "get different outcomes depending on who processes them, exposing institutions to "
         "fair lending violations."),
        ("Audit Trail Fragmentation",
         "Compliance Gap",
         "Reconstructing a decision for regulatory review requires pulling emails, system logs, "
         "manual notes, and database queries — an expensive, error-prone process that often "
         "fails to produce a coherent narrative."),
        ("Human Bottlenecks",
         "Scalability Limit",
         "Every step requires a human handoff. Scaling loan volume means scaling headcount "
         "proportionally. There is no path to exponential throughput improvement without "
         "fundamentally redesigning the process."),
    ]
    w1, w2, w3 = UW*0.32, UW*0.18, UW*0.50
    hdr = [P("<b>Pain Point</b>", S["th"]),
           P("<b>Severity</b>", S["th"]),
           P("<b>Description</b>", S["th"])]
    rows = [[P(t, S["td_b"]), P(s, S["td"]), P(d, S["td"])]
            for t, s, d in problems]
    story.append(data_table(hdr, rows, [w1, w2, w3], S))
    return story

def build_s3(S):
    story = [PageBreak(), sec_header("3.  The Solution", S), SP(0.3)]
    story.append(P(
        "Loan Shark replaces the fragmented, manual handoff chain with a structured "
        "9-agent AI pipeline. Each agent has a single, well-defined responsibility, "
        "receives structured input, performs its analysis using Groq's llama-3.3-70b-versatile "
        "LLM, and passes an enriched structured payload to the next agent via Band's "
        "messaging protocol.", S["body"]))

    story.append(P("Key Differentiators", S["h2"]))
    diffs = [
        ("Speed", "What takes 3-14 days in a traditional process completes in minutes. AI agents don't have queues, meetings, or lunch breaks."),
        ("Consistency", "Every application is evaluated against the exact same criteria in the exact same order. No human variance, no implicit bias."),
        ("Complete Context", "Each downstream agent receives everything its predecessors computed — enriched, structured, and validated. No information loss at handoffs."),
        ("Built-in Compliance", "A dedicated Compliance Agent applies RBI regulatory requirements as a hard gate. No approved application bypasses regulatory review."),
        ("Immutable Audit Trail", "The Band room history IS the audit trail. Every handoff, every flag, every decision note — timestamped and immutable."),
        ("Human Authority", "AI is advisory. The final decision always requires a human loan officer's signature. The system augments human judgment, not replaces it."),
    ]
    for title, desc in diffs:
        story.append(B(f"<b>{title}:</b>  {desc}", S))
    return story

def build_s4(S):
    story = [PageBreak(), sec_header("4.  System Architecture", S)]

    story.append(P("4.1  High-Level Overview", S["h2"]))
    story.append(P(
        "Loan Shark is composed of three primary layers: the Presentation Layer (Streamlit), "
        "the Agent Layer (9 independent Band agents), and the Coordination Layer (Band platform). "
        "These layers communicate exclusively through Band's messaging infrastructure.",
        S["body"]))
    w1, w2, w3 = UW*0.22, UW*0.22, UW*0.56
    hdr = [P("<b>Layer</b>", S["th"]),
           P("<b>Component</b>", S["th"]),
           P("<b>Responsibility</b>", S["th"])]
    rows = [
        [P("Presentation",  S["td_b"]), P("Streamlit UI",    S["td"]), P("Loan application form, real-time pipeline status, human gate interface", S["td"])],
        [P("Coordination",  S["td_b"]), P("Band Platform",   S["td"]), P("Message routing, @mention delivery, room history, WebSocket connections", S["td"])],
        [P("Agent (x9)",    S["td_b"]), P("Python + LangGraph", S["td"]), P("Domain-specific analysis, LLM inference via Groq, structured output", S["td"])],
        [P("LLM Backend",   S["td_b"]), P("Groq API",        S["td"]), P("Fast inference for all 9 agents using llama-3.3-70b-versatile", S["td"])],
    ]
    story.append(data_table(hdr, rows, [w1, w2, w3], S))

    story.append(P("4.2  Pipeline Architecture", S["h2"]))
    story.append(P(
        "The pipeline is a strict sequential chain. Each agent can only trigger the next; "
        "there is no branching, no parallelism, and no backtracking. This deliberate design "
        "ensures a consistent, auditable, and reproducible processing sequence.",
        S["body"]))
    story += code_block(
        "  Applicant fills form (Streamlit UI)\n"
        "        |\n"
        "        v  POST via Band REST API\n"
        "  [1] INTAKE AGENT           Validates & structures application\n"
        "        |  LOAN_APPLICATION: @DocumentAgent\n"
        "        v\n"
        "  [2] DOCUMENT AGENT         Doc completeness & consistency\n"
        "        |  DOC_VERIFICATION: @CreditAgent\n"
        "        v\n"
        "  [3] CREDIT AGENT           Credit profile & grade analysis\n"
        "        |  CREDIT_ANALYSIS: @FraudAgent\n"
        "        v\n"
        "  [4] FRAUD AGENT            Fraud signals & identity checks\n"
        "        |  FRAUD_REPORT: @RiskAgent\n"
        "        v\n"
        "  [5] RISK AGENT             DTI ratio & financial risk scoring\n"
        "        |  RISK_ASSESSMENT: @ComplianceAgent\n"
        "        v\n"
        "  [6] COMPLIANCE AGENT       RBI regulatory compliance check\n"
        "        |  COMPLIANCE_CHECK: @DecisionAgent\n"
        "        v\n"
        "  [7] DECISION AGENT         APPROVE / DENY / COUNTER_OFFER\n"
        "        |  LOAN_DECISION_READY: @PricingAgent\n"
        "        v\n"
        "  [8] PRICING AGENT          Interest rate, EMI, fees, terms\n"
        "        |  PRICING_TERMS: @CommunicationAgent\n"
        "        v\n"
        "  [9] COMMUNICATION AGENT    Formal sanction / rejection letter\n"
        "        |  FORMAL_LETTER_READY:\n"
        "        v\n"
        "  HUMAN LOAN OFFICER         Reviews AI recommendation & signs off",
        S, label="FULL PIPELINE FLOW DIAGRAM")

    story.append(P("4.3  Communication Model", S["h2"]))
    story.append(P(
        "All inter-agent communication occurs exclusively through Band's real-time messaging. "
        "Each agent is a persistent WebSocket connection to the Band platform. When an agent "
        "receives a message containing its trigger keyword, it wakes up, processes the payload "
        "using LangGraph + Groq, generates a response, and posts the next message with an "
        "@mention of the next agent. There is no shared memory, no message queue, no service bus, "
        "no database. The Band room is the single source of truth.", S["body"]))

    story.append(P("4.4  Data Enrichment Chain", S["h2"]))
    story.append(P(
        "Each agent receives the previous agent's complete JSON payload and extends it with its "
        "own computed fields before passing it forward. By Agent 9, the payload contains every "
        "field computed by every previous agent — a complete, structured application history "
        "in a single document.", S["body"]))
    w1, w2 = UW*0.30, UW*0.70
    hdr = [P("<b>After Agent</b>", S["th"]), P("<b>New Fields Added to Payload</b>", S["th"])]
    rows = [
        [P("[1] Intake",        S["td_b"]), P("application_id, validated schema, timestamp, currency",                            S["td"])],
        [P("[2] Document",      S["td_b"]), P("doc_verdict, doc_flags[], doc_completeness_score",                                  S["td"])],
        [P("[3] Credit",        S["td_b"]), P("credit_grade, credit_tier, max_lti, credit_behavior_notes",                        S["td"])],
        [P("[4] Fraud",         S["td_b"]), P("fraud_risk_level, fraud_flags[], fraud_confidence",                                 S["td"])],
        [P("[5] Risk",          S["td_b"]), P("risk_score, dti_before, dti_after, employment_risk, collateral_coverage + all prior fields", S["td"])],
        [P("[6] Compliance",    S["td_b"]), P("compliance_verdict, violations[], regulatory_notes",                                S["td"])],
        [P("[7] Decision",      S["td_b"]), P("recommendation, approved_amount, confidence, decision_basis, compliance_notes",     S["td"])],
        [P("[8] Pricing",       S["td_b"]), P("interest_rate, processing_fee, emi, prepayment_terms, insurance_premium",           S["td"])],
        [P("[9] Communication", S["td_b"]), P("letter_type, letter_body (full formatted letter text)",                             S["td"])],
    ]
    story.append(data_table(hdr, rows, [w1, w2], S))
    return story

def build_s5(S):
    story = [PageBreak(), sec_header("5.  The 9-Agent Pipeline", S)]
    story.append(P(
        "Each agent is an independent Python process. It connects to the Band platform via "
        "WebSocket, listens for its trigger keyword, performs its domain-specific analysis "
        "using LangGraph and Groq, then posts its structured output back to the Band room "
        "with an @mention of the next agent. All 9 run simultaneously — each sleeping until "
        "its keyword appears.", S["body"]))

    # ── Agent 1
    story.append(SP(0.2))
    story.append(agent_box(1, "Intake Agent",
        "NEW_LOAN_APPLICATION:", "LOAN_APPLICATION: @DocumentAgent", S))
    story.append(SP(0.1))
    story.append(P(
        "The gatekeeper of the pipeline. Receives raw, unstructured application data submitted "
        "via the Streamlit UI and performs the first line of validation and structuring. "
        "If validation fails, it fires INTAKE_ERROR: and halts the pipeline immediately, "
        "preventing corrupt data from propagating through the remaining 8 agents.", S["body"]))
    story.append(P("Responsibilities:", S["h4"]))
    for r in [
        "Validates all required fields are present (name, age, income, loan amount, purpose, tenure)",
        "Sanity-checks values: age 18-70, income > 0, loan amount within plausible bounds",
        "Detects logical errors (e.g. claiming 20 years employment at age 22)",
        "Generates a unique application_id (format: APP-{timestamp})",
        "Normalizes currency representation and numeric fields",
        "Formats raw text into a structured LoanApplication JSON schema",
        "On failure: fires INTAKE_ERROR: with detailed error code and halts pipeline",
    ]:
        story.append(B(r, S))

    # ── Agent 2
    story.append(SP(0.3))
    story.append(agent_box(2, "Document Verification Agent",
        "LOAN_APPLICATION:", "DOC_VERIFICATION: @CreditAgent", S))
    story.append(SP(0.1))
    story.append(P(
        "Checks document completeness and internal consistency without connecting to any "
        "external database. Its analysis is entirely logical — cross-referencing claimed "
        "employment type against expected documentation requirements.", S["body"]))
    story.append(P("Document Requirements by Employment Type:", S["h4"]))
    w1, w2 = UW*0.30, UW*0.70
    hdr = [P("<b>Employment Type</b>", S["th"]), P("<b>Required Documents</b>", S["th"])]
    rows = [
        [P("Salaried",       S["td_b"]), P("Salary slips (3 months), employee ID, bank statements (6 months), employer letter", S["td"])],
        [P("Self-Employed",  S["td_b"]), P("ITR (2 years), business registration certificate, GST registration, bank statements", S["td"])],
        [P("Business Owner", S["td_b"]), P("Company registration, audited financials (2 years), ITR, bank statements", S["td"])],
        [P("Unemployed",     S["td_b"]), P("Alternate income proof (rental income, investments), bank statements", S["td"])],
    ]
    story.append(data_table(hdr, rows, [w1, w2], S))
    story.append(P(
        "Output fields: doc_verdict (COMPLETE / PARTIAL / INSUFFICIENT), "
        "doc_completeness_score (0-100), doc_flags[] with specific issues identified.", S["body_l"]))

    # ── Agent 3
    story.append(SP(0.3))
    story.append(agent_box(3, "Credit Analysis Agent",
        "DOC_VERIFICATION:", "CREDIT_ANALYSIS: @FraudAgent", S))
    story.append(SP(0.1))
    story.append(P(
        "Interprets the raw CIBIL/credit score into a full credit profile. "
        "Determines creditworthiness tier and the maximum exposure the institution "
        "should be willing to take for this applicant.", S["body"]))
    story.append(P("Credit Grade Mapping:", S["h4"]))
    w1, w2, w3, w4 = UW*0.22, UW*0.12, UW*0.24, UW*0.42
    hdr = [P("<b>Score Range</b>", S["th"]), P("<b>Grade</b>", S["th"]),
           P("<b>Risk Tier</b>", S["th"]), P("<b>Max Loan-to-Income</b>", S["th"])]
    rows = [
        [P("750 - 900",     S["td"]), P("A+",  S["td_b"]), P("Prime",              S["td"]), P("Up to 5x monthly income",    S["td"])],
        [P("700 - 749",     S["td"]), P("A",   S["td_b"]), P("Near-Prime",         S["td"]), P("Up to 4x monthly income",    S["td"])],
        [P("650 - 699",     S["td"]), P("B",   S["td_b"]), P("Subprime",           S["td"]), P("Up to 3x monthly income",    S["td"])],
        [P("600 - 649",     S["td"]), P("C",   S["td_b"]), P("High Risk",          S["td"]), P("Up to 2x monthly income",    S["td"])],
        [P("550 - 599",     S["td"]), P("D",   S["td_b"]), P("Very High Risk",     S["td"]), P("Up to 1.5x monthly income",  S["td"])],
        [P("Below 550",     S["td"]), P("F",   S["td_b"]), P("Decline Territory",  S["td"]), P("Hard decline recommended",   S["td"])],
        [P("Not Provided",  S["td"]), P("N/A", S["td_b"]), P("First-Time Borrower",S["td"]), P("Max 1x monthly income",     S["td"])],
    ]
    story.append(data_table(hdr, rows, [w1, w2, w3, w4], S))

    # ── Agent 4
    story.append(SP(0.3))
    story.append(agent_box(4, "Fraud Detection Agent",
        "CREDIT_ANALYSIS:", "FRAUD_REPORT: @RiskAgent", S))
    story.append(SP(0.1))
    story.append(P(
        "The pattern recognition specialist. Analyzes the complete application for fraud "
        "signals, inconsistencies, and high-risk behavioral patterns that suggest the "
        "application may be fraudulent, synthetic, or part of a loan stacking scheme.",
        S["body"]))
    story.append(P("Fraud Signal Categories Checked:", S["h4"]))
    fraud_signals = [
        ("Income Anomalies", "Income claims disproportionate to employment type, age, or sector norms. Self-employed applicants claiming corporate-level income with no business registration details."),
        ("Identity Inconsistencies", "Mismatched employment tenure vs. age. Claimed education level inconsistent with income. Employer-address combinations geographically implausible."),
        ("Loan Stacking Indicators", "Existing debt levels suggesting multiple concurrent loan applications. DTI at intake that implies prior undisclosed credit facilities."),
        ("Synthetic Identity Signals", "No credit history combined with high income claims. Perfect documentation on an otherwise high-risk profile. Unusually long tenure at unknown companies."),
        ("Application Velocity Patterns", "Loan amount at suspiciously round numbers. Purpose codes inconsistent with the amount/tenure requested."),
    ]
    w1, w2 = UW*0.28, UW*0.72
    hdr = [P("<b>Category</b>", S["th"]), P("<b>What the Agent Checks</b>", S["th"])]
    rows = [[P(c, S["td_b"]), P(d, S["td"])] for c, d in fraud_signals]
    story.append(data_table(hdr, rows, [w1, w2], S))
    story.append(P(
        "Output: fraud_risk_level (LOW / MEDIUM / HIGH / CRITICAL) and fraud_flags[] "
        "array with specific flag codes and human-readable reasoning.", S["body_l"]))

    # ── Agent 5
    story.append(SP(0.3))
    story.append(agent_box(5, "Risk Assessment Agent",
        "FRAUD_REPORT:", "RISK_ASSESSMENT: @ComplianceAgent", S))
    story.append(SP(0.1))
    story.append(P(
        "The financial modeler and data aggregator. Performs quantitative risk scoring using "
        "DTI analysis, employment stability assessment, and collateral valuation. Also carries "
        "forward ALL structured fields from Agents 1-4 so downstream agents have complete "
        "context without back-referencing earlier messages.", S["body"]))
    story.append(P("Calculations Performed:", S["h4"]))
    calcs = [
        "DTI Before Loan:  (existing_monthly_debt / monthly_income) x 100",
        "DTI After Loan:   ((existing_monthly_debt + estimated_emi) / monthly_income) x 100",
        "Employment Stability Score:  Weighted (tenure, employment type, employer size)",
        "Collateral Coverage Ratio:   Estimated collateral value / loan amount requested",
        "Composite Risk Score (0-100): Weighted avg of credit grade + DTI + fraud level + employment + doc completeness",
        "Risk Category:   LOW (0-30) / MEDIUM (31-55) / HIGH (56-75) / CRITICAL (76-100)",
    ]
    for c in calcs:
        story.append(B(c, S))

    # ── Agent 6
    story.append(SP(0.3))
    story.append(agent_box(6, "Compliance Agent",
        "RISK_ASSESSMENT:", "COMPLIANCE_CHECK: @DecisionAgent", S))
    story.append(SP(0.1))
    story.append(P(
        "The regulatory guardrail. Validates the application against RBI lending guidelines "
        "and fair lending principles. Its verdict can block an application regardless of "
        "positive credit or risk scores — it is the one agent whose hard block cannot be "
        "overridden by the AI pipeline.", S["body"]))
    story.append(P("RBI Guidelines Applied:", S["h4"]))
    rbi = [
        ("DTI Cap", "Post-loan DTI must not exceed 50% for personal/vehicle loans, 60% for home loans with collateral"),
        ("KYC Requirements", "All mandatory identity and income documents must be present per employment type"),
        ("Sector Exposure Limits", "Loan purpose cross-checked against RBI sector exposure guidelines"),
        ("Minimum Income Floor", "Monthly income must be sufficient to cover EMI with a minimum 20% buffer remaining"),
        ("Age-Tenure Alignment", "Loan tenure must not extend beyond retirement age (65) for salaried employees"),
        ("Fair Lending Check", "Flags if any combination of factors could constitute discriminatory lending"),
        ("Maximum LTV Ratio", "For secured loans, loan amount must not exceed 80% of estimated collateral value"),
    ]
    w1, w2 = UW*0.28, UW*0.72
    hdr = [P("<b>Guideline</b>", S["th"]), P("<b>Rule Applied</b>", S["th"])]
    rows = [[P(g, S["td_b"]), P(r, S["td"])] for g, r in rbi]
    story.append(data_table(hdr, rows, [w1, w2], S))

    # ── Agent 7
    story.append(SP(0.3))
    story.append(agent_box(7, "Decision Agent",
        "COMPLIANCE_CHECK:", "LOAN_DECISION_READY: @PricingAgent", S))
    story.append(SP(0.1))
    story.append(P(
        "Applies a deterministic decision matrix to the full context from all 6 upstream agents. "
        "Produces the official lending recommendation with full compliance documentation. "
        "Every decision is accompanied by a compliance audit note citing the specific rule "
        "or factor combination that triggered it.", S["body"]))
    story.append(P("Decision Matrix:", S["h4"]))
    w1, w2 = UW*0.50, UW*0.50
    hdr = [P("<b>Condition</b>", S["th"]), P("<b>Decision</b>", S["th"])]
    rows = [
        [P("compliance_verdict == NON_COMPLIANT", S["td"]),      P("DENY  (hard block - regulatory)",         S["td_b"])],
        [P("fraud_risk_level == CRITICAL",         S["td"]),      P("DENY  (hard block - fraud)",              S["td_b"])],
        [P("credit_grade == F",                    S["td"]),      P("DENY  (hard block - creditworthiness)",   S["td_b"])],
        [P("DTI after loan > 70%",                 S["td"]),      P("DENY  (hard block - affordability)",      S["td_b"])],
        [P("All hard blocks clear AND risk_score <= 40", S["td"]),P("APPROVE",                                 S["td_b"])],
        [P("All clear AND risk_score 41-65",       S["td"]),      P("COUNTER_OFFER (reduced amount/tenure)",   S["td_b"])],
        [P("Any soft flag AND risk_score > 65",    S["td"]),      P("DENY  (with improvement guidance)",       S["td_b"])],
    ]
    story.append(data_table(hdr, rows, [w1, w2], S))

    # ── Agent 8
    story.append(SP(0.3))
    story.append(agent_box(8, "Pricing Agent",
        "LOAN_DECISION_READY:", "PRICING_TERMS: @CommunicationAgent", S))
    story.append(SP(0.1))
    story.append(P(
        "The actuary. Calculates exact financial terms within the parameters established "
        "by the Decision Agent, personalizing the offer to the specific risk profile "
        "of the applicant.", S["body"]))
    story.append(P("Pricing Calculations:", S["h4"]))
    for item in [
        "Base rate:  RBI repo rate + credit grade spread",
        "Risk premium:  Added based on risk_score band",
        "Final interest rate:  Base rate + credit spread + risk premium",
        "Processing fee:  0.5-2% of loan amount based on loan type and risk",
        "Monthly EMI:  Standard amortization formula using principal, rate, and tenure",
        "Insurance premium:  If mandatory, based on loan amount and tenure",
        "Prepayment penalty structure:  0-2% of outstanding principal based on remaining tenure",
        "COUNTER_OFFER path:  All terms recalculated for the modified amount and tenure",
    ]:
        story.append(B(item, S))

    # ── Agent 9
    story.append(SP(0.3))
    story.append(agent_box(9, "Communication Agent",
        "PRICING_TERMS:", "FORMAL_LETTER_READY: -> Human Gate", S))
    story.append(SP(0.1))
    story.append(P(
        "The writer. Drafts the formal, legally-worded correspondence that will be sent "
        "to the applicant. Critically, this agent does NOT dispatch letters autonomously — "
        "the draft goes to the Human Gate for loan officer review and signature.",
        S["body"]))
    w1, w2 = UW*0.28, UW*0.72
    hdr = [P("<b>Letter Type</b>", S["th"]), P("<b>Contents</b>", S["th"])]
    rows = [
        [P("Loan Sanction Letter\n(APPROVE / COUNTER_OFFER)", S["td_b"]),
         P("Formal header (Loan Shark Financial Services), applicant salutation, congratulatory "
           "opening, all approved financial terms (amount / tenure / rate / EMI / fee), "
           "key conditions (3-4 bullet points), next steps for document submission, "
           "legal disclaimer, officer signature block", S["td"])],
        [P("Regret Letter\n(DENY)", S["td_b"]),
         P("Professional empathetic tone, specific denial reasons in regulatory language, "
           "guidance on improving eligibility (credit score improvement, debt reduction), "
           "timeline for re-application, grievance redressal information", S["td"])],
    ]
    story.append(data_table(hdr, rows, [w1, w2], S))
    return story

def build_s6(S):
    story = [PageBreak(), sec_header("6.  Message Protocol &amp; Data Schema", S)]

    story.append(P("6.1  Message Format", S["h2"]))
    story.append(P(
        "Each agent communicates by posting a structured message to the Band room. "
        "The message has two parts: a plain-text header with the message tag and @mention, "
        "and a JSON payload embedded in a markdown code fence.", S["body"]))
    story += code_block(
        'LOAN_APPLICATION: Application ID: APP-123456\n'
        '@DocumentAgent please verify this application.\n\n'
        '```json\n'
        '{\n'
        '  "message_type": "LOAN_APPLICATION",\n'
        '  "application_id": "APP-123456",\n'
        '  "applicant_name": "Priya Sharma",\n'
        '  "applicant_age": 32,\n'
        '  "monthly_income": 120000.0,\n'
        '  "currency": "INR",\n'
        '  "employment_type": "salaried",\n'
        '  "employer_name": "Infosys Ltd",\n'
        '  "years_employed": 5.0,\n'
        '  "loan_amount_requested": 800000.0,\n'
        '  "loan_purpose": "home",\n'
        '  "loan_tenure_months": 120,\n'
        '  "existing_debt_monthly": 8000.0,\n'
        '  "credit_score": 768,\n'
        '  "collateral_offered": "Residential property in Bengaluru"\n'
        '}\n'
        '```',
        S, label="EXAMPLE: Intake Agent Output Message")

    story.append(P("6.2  Full Message Tag Reference", S["h2"]))
    w1, w2, w3, w4 = UW*0.26, UW*0.18, UW*0.18, UW*0.38
    hdr = [P("<b>Message Tag</b>", S["th"]), P("<b>Sender</b>", S["th"]),
           P("<b>Receiver</b>", S["th"]), P("<b>Key Fields Added</b>", S["th"])]
    rows = [
        [P("NEW_LOAN_APPLICATION:", S["td_b"]), P("Streamlit UI",      S["td"]), P("IntakeAgent",        S["td"]), P("Raw form data as plain text",                       S["td"])],
        [P("LOAN_APPLICATION:",     S["td_b"]), P("IntakeAgent",       S["td"]), P("DocumentAgent",      S["td"]), P("application_id, validated schema",                  S["td"])],
        [P("DOC_VERIFICATION:",     S["td_b"]), P("DocumentAgent",     S["td"]), P("CreditAgent",        S["td"]), P("doc_verdict, doc_flags[], doc_completeness_score",   S["td"])],
        [P("CREDIT_ANALYSIS:",      S["td_b"]), P("CreditAgent",       S["td"]), P("FraudAgent",         S["td"]), P("credit_grade, credit_tier, max_lti",                S["td"])],
        [P("FRAUD_REPORT:",         S["td_b"]), P("FraudAgent",        S["td"]), P("RiskAgent",          S["td"]), P("fraud_risk_level, fraud_flags[], fraud_confidence",  S["td"])],
        [P("RISK_ASSESSMENT:",      S["td_b"]), P("RiskAgent",         S["td"]), P("ComplianceAgent",    S["td"]), P("risk_score, dti_before, dti_after + all prior",     S["td"])],
        [P("COMPLIANCE_CHECK:",     S["td_b"]), P("ComplianceAgent",   S["td"]), P("DecisionAgent",      S["td"]), P("compliance_verdict, violations[]",                  S["td"])],
        [P("LOAN_DECISION_READY:",  S["td_b"]), P("DecisionAgent",     S["td"]), P("PricingAgent",       S["td"]), P("recommendation, approved_amount, confidence",        S["td"])],
        [P("PRICING_TERMS:",        S["td_b"]), P("PricingAgent",      S["td"]), P("CommunicationAgent", S["td"]), P("interest_rate, emi, processing_fee",                S["td"])],
        [P("FORMAL_LETTER_READY:",  S["td_b"]), P("CommunicationAgent",S["td"]), P("Human Gate",         S["td"]), P("letter_body, letter_type",                          S["td"])],
        [P("INTAKE_ERROR:",         S["td_b"]), P("IntakeAgent",       S["td"]), P("Human / System",     S["td"]), P("error_code, error_detail (HALTS pipeline)",         S["td"])],
    ]
    story.append(data_table(hdr, rows, [w1, w2, w3, w4], S))
    return story

def build_s7(S):
    story = [PageBreak(), sec_header("7.  Technology Stack", S)]

    story.append(P("7.1  Band SDK", S["h2"]))
    story.append(P(
        "Band SDK is the core coordination infrastructure. It provides the real-time WebSocket "
        "connections that allow agents to listen for and publish messages in a shared room. "
        "The @mention protocol is the sole mechanism by which agents hand off work to each other.",
        S["body"]))
    band_items = [
        ("band.Agent", "Base class for all 9 agents — handles WebSocket lifecycle, reconnection, and message dispatch"),
        ("band.adapters.LangGraphAdapter", "Bridges Band message events to LangGraph's agent graph execution model"),
        ("band.config.load_agent_config", "Loads agent UUID and API key from agent_config.yaml"),
        ("WebSocket URL", "wss://app.band.ai/api/v1/socket/websocket"),
        ("REST API URL", "https://app.band.ai/ — used by Streamlit to post the initial application"),
    ]
    w1, w2 = UW*0.35, UW*0.65
    hdr = [P("<b>Component</b>", S["th"]), P("<b>Purpose</b>", S["th"])]
    rows = [[P(k, S["td_b"]), P(v, S["td"])] for k, v in band_items]
    story.append(data_table(hdr, rows, [w1, w2], S))

    story.append(P("7.2  LangGraph", S["h2"]))
    story.append(P(
        "LangGraph provides the agent execution runtime. Each agent is implemented as a "
        "LangGraph StateGraph with nodes for input parsing, LLM inference, output validation, "
        "and message posting. The InMemorySaver checkpointer maintains state within a session.",
        S["body"]))

    story.append(P("7.3  Groq LLM", S["h2"]))
    story.append(P(
        "All 9 agents use Groq's llama-3.3-70b-versatile model via LangChain's ChatOpenAI "
        "interface (Groq is OpenAI-API-compatible). Groq's inference speed is critical — "
        "it enables the full 9-agent pipeline to complete in under 2 minutes.", S["body"]))
    story += code_block(
        'llm = ChatOpenAI(\n'
        '    model="llama-3.3-70b-versatile",\n'
        '    openai_api_key=os.getenv("GROQ_API_KEY"),\n'
        '    openai_api_base="https://api.groq.com/openai/v1",\n'
        '    temperature=0.1,   # Low: consistent, structured outputs\n'
        '    max_tokens=2048,\n'
        ')', S, label="LLM CONFIGURATION (same across all 9 agents)")

    story.append(P("7.4  Streamlit Frontend", S["h2"]))
    story.append(P(
        "The Streamlit application serves as both the loan application interface and the "
        "real-time pipeline monitoring dashboard. Uses Streamlit's session_state to track "
        "pipeline status, agent messages, and decision data across reruns.", S["body"]))

    story.append(P("7.5  Package Management — uv", S["h2"]))
    story.append(P(
        "uv provides deterministic dependency resolution via uv.lock, "
        "fast installation, and the 'uv run' prefix for all Python script execution.",
        S["body"]))

    w1, w2, w3 = UW*0.28, UW*0.18, UW*0.54
    hdr = [P("<b>Package</b>", S["th"]), P("<b>Version</b>", S["th"]), P("<b>Purpose</b>", S["th"])]
    rows = [
        [P("band-sdk",         S["td_b"]), P("latest",  S["td"]), P("Agent framework + WebSocket + @mention protocol", S["td"])],
        [P("langchain-openai", S["td_b"]), P("latest",  S["td"]), P("OpenAI-compatible LLM client interface to Groq",  S["td"])],
        [P("langgraph",        S["td_b"]), P("latest",  S["td"]), P("Agent state machine and graph execution runtime", S["td"])],
        [P("streamlit",        S["td_b"]), P("latest",  S["td"]), P("Web UI framework",                               S["td"])],
        [P("python-dotenv",    S["td_b"]), P("latest",  S["td"]), P("Environment variable loading from .env",          S["td"])],
        [P("pyyaml",           S["td_b"]), P("latest",  S["td"]), P("agent_config.yaml parsing",                      S["td"])],
        [P("requests",         S["td_b"]), P("latest",  S["td"]), P("Band REST API calls from Streamlit",             S["td"])],
        [P("reportlab",        S["td_b"]), P("4.5.1",  S["td"]), P("PDF documentation generation",                   S["td"])],
    ]
    story.append(data_table(hdr, rows, [w1, w2, w3], S))
    return story

def build_s8(S):
    story = [PageBreak(), sec_header("8.  Compliance &amp; Regulatory Framework", S)]
    story.append(P(
        "Compliance is a first-class architectural concern in Loan Shark. The system enforces "
        "regulatory requirements at multiple levels, with different enforcement strengths for "
        "different rule types.", S["body"]))

    story.append(P("8.1  Hard Blocks vs Soft Flags", S["h2"]))
    w1, w2, w3, w4 = UW*0.18, UW*0.22, UW*0.18, UW*0.42
    hdr = [P("<b>Type</b>", S["th"]), P("<b>Effect</b>", S["th"]),
           P("<b>Override?</b>", S["th"]), P("<b>Examples</b>", S["th"])]
    rows = [
        [P("Hard Block",  S["td_b"]), P("Automatic DENY",          S["td"]), P("Human only",       S["td"]), P("Regulatory violation, CRITICAL fraud level, Grade F credit, DTI > 70%", S["td"])],
        [P("Soft Flag",   S["td_b"]), P("Reduces approval probability", S["td"]), P("Decision Agent",  S["td"]), P("MEDIUM fraud risk, PARTIAL documents, HIGH risk score (56-75)", S["td"])],
        [P("Warning",     S["td_b"]), P("Logged in audit trail",   S["td"]), P("Automatic",        S["td"]), P("Unusual income claim, first-time borrower, missing collateral on borderline loan", S["td"])],
    ]
    story.append(data_table(hdr, rows, [w1, w2, w3, w4], S))

    story.append(P("8.2  RBI Guidelines Implemented", S["h2"]))
    rbi_detail = [
        ("DTI Threshold Enforcement",
         "The Compliance Agent applies maximum Debt-to-Income ratios: 50% for unsecured loans "
         "(personal, vehicle, education), 60% for secured home loans. Applications breaching "
         "these thresholds receive a hard block regardless of credit score."),
        ("KYC Verification Requirements",
         "Employment-type-specific document requirements are enforced. Salaried employees must "
         "provide salary slips and employment verification; self-employed must have ITR and business "
         "registration; all applicants require valid government photo ID."),
        ("Age-Tenure Alignment Rule",
         "For salaried applicants, the loan tenure must not extend beyond the standard retirement "
         "age of 65. A 55-year-old cannot receive a 15-year salaried home loan product."),
        ("Minimum Income Requirements",
         "Post-EMI take-home income must not fall below 40% of gross monthly income. Applications "
         "where the proposed EMI would breach this threshold are blocked."),
        ("Sector Exposure Guidelines",
         "The compliance agent checks whether the loan purpose falls under any RBI sector-specific "
         "exposure caps (e.g. real estate, commercial vehicle). High-exposure sectors trigger "
         "additional scrutiny flags."),
    ]
    for title, desc in rbi_detail:
        story.append(P(f"<b>{title}</b>", S["h4"]))
        story.append(P(desc, S["body"]))

    story.append(P("8.3  Fair Lending Checks", S["h2"]))
    story.append(P(
        "The Compliance Agent includes a fair lending verification step. It checks that the "
        "combination of factors used in the recommendation could not be construed as indirectly "
        "discriminatory under Indian fair lending regulations. Decisions must be defensible on "
        "purely financial grounds. Any decision that appears to penalize an applicant on "
        "non-financial grounds is flagged with a FAIR_LENDING_REVIEW code.", S["body"]))
    return story

def build_s9(S):
    story = [PageBreak(), sec_header("9.  Human-in-the-Loop Design", S)]
    story.append(P(
        "Human oversight is the non-negotiable design principle of Loan Shark. The AI pipeline "
        "is an advisor and accelerator, not a decision-maker. No loan can be approved, denied, "
        "or disbursed without a human loan officer's explicit authorization.", S["body"]))

    story.append(P("The Human Gate — What the Loan Officer Sees", S["h2"]))
    story.append(P(
        "When the Communication Agent posts FORMAL_LETTER_READY:, the Streamlit application "
        "enters the Human Gate state. The loan officer is presented with:", S["body"]))
    gate_items = [
        "Decision summary card:  Recommendation badge (APPROVE / DENY / COUNTER_OFFER), application ID, risk category, and AI confidence score",
        "Key financial metrics:  Approved loan amount, tenure, estimated monthly EMI",
        "Counter-offer terms (if applicable):  Modified amount, rate band, and reasoning",
        "Denial reasons (if applicable):  Specific flags that triggered denial in plain language",
        "Full formal letter preview:  Complete, scroll-able bank letter draft as formatted by the Communication Agent",
        "Compliance & audit trail:  Full compliance notes from Agent 6 in an expandable section",
        "Two action buttons:  'Approve & Finalize' (primary) and 'Reject / Override' (secondary)",
    ]
    for item in gate_items:
        story.append(B(item, S))

    story.append(P("Override Authority", S["h2"]))
    story.append(P(
        "The human loan officer retains full authority to override any AI recommendation. "
        "Clicking 'Reject / Override' on an APPROVE recommendation is fully supported. "
        "All overrides are logged in the agent message feed with timestamp and action type. "
        "The institution's credit policy may require senior officer sign-off for overrides "
        "of hard-block decisions.", S["body"]))

    story.append(P("Audit Trail Completeness", S["h2"]))
    story.append(P(
        "The Band room history provides a complete, timestamped audit trail: every agent's "
        "analysis, every flag raised, the exact recommendation with its basis, and the human "
        "officer's final action. This is sufficient for RBI examination, internal audit, and "
        "any applicant grievance resolution.", S["body"]))
    return story

def build_s10(S):
    story = [PageBreak(), sec_header("10.  Frontend — Streamlit Application", S)]
    story.append(P(
        "The Streamlit application (app.py) is a single-page application with a two-column layout: "
        "application form on the left, pipeline tracker and agent feed on the right.",
        S["body"]))

    story.append(P("Application Form Fields", S["h2"]))
    w1, w2, w3 = UW*0.28, UW*0.22, UW*0.50
    hdr = [P("<b>Field</b>", S["th"]), P("<b>Type</b>", S["th"]), P("<b>Validation</b>", S["th"])]
    rows = [
        [P("Full Name",          S["td_b"]), P("Text input",        S["td"]), P("Required, non-empty",                           S["td"])],
        [P("Age",                S["td_b"]), P("Number (18-70)",    S["td"]), P("Must be between 18 and 70",                     S["td"])],
        [P("Credit Score",       S["td_b"]), P("Number (0-900)",    S["td"]), P("0 = unknown; maps to first-time borrower path", S["td"])],
        [P("Currency",           S["td_b"]), P("Selectbox",         S["td"]), P("INR / USD",                                     S["td"])],
        [P("Employment Type",    S["td_b"]), P("Selectbox",         S["td"]), P("salaried / self_employed / business_owner / unemployed", S["td"])],
        [P("Employer Name",      S["td_b"]), P("Text input",        S["td"]), P("Required for salaried/self-employed",           S["td"])],
        [P("Monthly Income",     S["td_b"]), P("Number > 0",        S["td"]), P("Must be positive",                             S["td"])],
        [P("Years at Job",       S["td_b"]), P("Number (0-40)",     S["td"]), P("Cross-checked against applicant age",          S["td"])],
        [P("Loan Amount",        S["td_b"]), P("Number > 10,000",   S["td"]), P("Minimum loan threshold enforced",              S["td"])],
        [P("Loan Purpose",       S["td_b"]), P("Selectbox",         S["td"]), P("home / vehicle / education / personal / business", S["td"])],
        [P("Tenure",             S["td_b"]), P("Slider (6-360 mo)", S["td"]), P("Step size: 6 months",                         S["td"])],
        [P("Existing Debt/mo",   S["td_b"]), P("Number >= 0",       S["td"]), P("Used in DTI calculation by Risk Agent",        S["td"])],
        [P("Collateral",         S["td_b"]), P("Text input",        S["td"]), P("Optional but affects risk score and terms",    S["td"])],
    ]
    story.append(data_table(hdr, rows, [w1, w2, w3], S))

    story.append(P("Quick Demo Scenarios", S["h2"]))
    story.append(P(
        "Three pre-built demo scenarios allow instant demonstration without manual data entry. "
        "Clicking a demo button pre-fills all form fields with a carefully designed test case.",
        S["body"]))
    w1, w2, w3, w4 = UW*0.18, UW*0.22, UW*0.38, UW*0.22
    hdr = [P("<b>Button</b>", S["th"]), P("<b>Applicant</b>", S["th"]),
           P("<b>Profile</b>", S["th"]), P("<b>Expected Outcome</b>", S["th"])]
    rows = [
        [P("Good Applicant",  S["td_b"]), P("Priya Sharma, 32", S["td"]), P("Salaried, Rs.1.2L/mo, CIBIL 768, home loan, collateral",            S["td"]), P("APPROVE",        S["td_b"])],
        [P("Borderline",      S["td_b"]), P("Arjun Mehta, 28",  S["td"]), P("Self-employed, Rs.55K/mo, CIBIL 648, vehicle loan, no collateral",   S["td"]), P("COUNTER_OFFER",  S["td_b"])],
        [P("High Risk",       S["td_b"]), P("Ravi Kumar, 45",   S["td"]), P("Unemployed, Rs.30K/mo, no credit score, personal loan",              S["td"]), P("DENY",           S["td_b"])],
    ]
    story.append(data_table(hdr, rows, [w1, w2, w3, w4], S))

    story.append(P("Pipeline Tracker", S["h2"]))
    story.append(P(
        "The right column displays a 9-card vertical pipeline tracker. Each card shows the "
        "agent name and current status, updating dynamically as messages are processed: "
        "Waiting (grey) -> Processing (cyan, active border glow) -> Complete (green). "
        "The tracker uses detect_message_stage() to classify each pasted message.", S["body"]))

    story.append(P("Human Gate Interface", S["h2"]))
    story.append(P(
        "When FORMAL_LETTER_READY: is detected, the pipeline tracker enters awaiting_approval "
        "state. The human gate section renders below the agent feed with: decision summary, "
        "financial metrics (loan amount, tenure, EMI), formal letter preview rendered in "
        "Georgia serif font in a scrollable container, compliance audit trail, and the "
        "two action buttons.", S["body"]))
    return story

def build_s11(S):
    story = [PageBreak(), sec_header("11.  Setup &amp; Deployment Guide", S)]

    story.append(P("Prerequisites", S["h2"]))
    w1, w2, w3 = UW*0.25, UW*0.20, UW*0.55
    hdr = [P("<b>Requirement</b>", S["th"]), P("<b>Version</b>", S["th"]), P("<b>Notes</b>", S["th"])]
    rows = [
        [P("Python",       S["td_b"]), P("3.11+",  S["td"]), P("3.13.x recommended. Must be installed and in PATH.",      S["td"])],
        [P("uv",           S["td_b"]), P("latest", S["td"]), P("pip install uv  OR  winget install astral-sh.uv",          S["td"])],
        [P("Groq API Key", S["td_b"]), P("Free",   S["td"]), P("Register at console.groq.com — free tier available",       S["td"])],
        [P("Band Account", S["td_b"]), P("Pro",    S["td"]), P("app.band.ai — use promo code BANDHACK26 for free Pro access", S["td"])],
        [P("Git",          S["td_b"]), P("Any",    S["td"]), P("For cloning the repository",                                S["td"])],
    ]
    story.append(data_table(hdr, rows, [w1, w2, w3], S))

    story.append(P("Step-by-Step Installation", S["h2"]))
    steps = [
        ("Step 1 — Clone the repository",
         "git clone https://github.com/Ares19v/Loan_Shark.git\ncd Loan_Shark"),
        ("Step 2 — Install all dependencies",
         "uv sync"),
        ("Step 3 — Configure environment",
         "copy .env.example .env\n# Edit .env and fill in:\n#   GROQ_API_KEY=your-key-here\n#   BAND_ROOM_ID=your-room-id-here"),
        ("Step 4 — Run preflight check",
         "uv run python preflight.py\n# Fix any FAIL items before proceeding"),
        ("Step 5 — Create Band agents",
         "# On app.band.ai:\n# 1. Create 9 agents: IntakeAgent, DocumentAgent, CreditAgent,\n"
         "#    FraudAgent, RiskAgent, ComplianceAgent, DecisionAgent,\n"
         "#    PricingAgent, CommunicationAgent\n"
         "# 2. Create one room named 'LoanShark' and add all 9 agents\n"
         "# 3. Copy each agent's UUID and API key into agent_config.yaml"),
        ("Step 6 — Launch all 9 agents (one command)",
         "uv run python run_all.py"),
        ("Step 7 — Launch the Streamlit UI",
         "uv run streamlit run app.py\n# Opens at http://localhost:8501"),
    ]
    for label, cmd in steps:
        story.append(P(f"<b>{label}</b>", S["h4"]))
        story += code_block(cmd, S)
    return story

def build_s12(S):
    story = [PageBreak(), sec_header("12.  Quality Assurance — Preflight Check", S)]
    story.append(P(
        "preflight.py is a 94-assertion system validation script inspired by aviation "
        "preflight checklists. It validates every component of the system before launch "
        "and exits with code 0 (all clear) or code 1 (failures found).", S["body"]))

    w1, w2, w3 = UW*0.30, UW*0.12, UW*0.58
    hdr = [P("<b>Category</b>", S["th"]), P("<b>Checks</b>", S["th"]), P("<b>What It Validates</b>", S["th"])]
    rows = [
        [P("1. Python & Runtime",   S["td_b"]), P("9",  S["td"]), P("Python >= 3.11, all 7 required packages importable",                                  S["td"])],
        [P("2. File Structure",     S["td_b"]), P("20", S["td"]), P("All 20 required project files exist on disk",                                          S["td"])],
        [P("3. Environment Vars",   S["td_b"]), P("4",  S["td"]), P(".env populated, no placeholder values remaining",                                      S["td"])],
        [P("4. Agent Config",       S["td_b"]), P("10", S["td"]), P("agent_config.yaml valid YAML, all 9 agents have UUID and API key",                     S["td"])],
        [P("5. Python Syntax",      S["td_b"]), P("13", S["td"]), P("AST-parse all 13 Python source files — zero syntax errors",                            S["td"])],
        [P("6. Pipeline Chain",     S["td_b"]), P("9",  S["td"]), P("Each agent file has correct trigger keyword, @mention, and output tag",                 S["td"])],
        [P("7. Streamlit App",      S["td_b"]), P("16", S["td"]), P("All 9 message types detected, all 9 stages displayed, demo scenarios present",         S["td"])],
        [P("8. Branding",           S["td_b"]), P("9",  S["td"]), P("No stale 'LoanPilot' references in any file across the codebase",                     S["td"])],
        [P("9. API Connectivity",   S["td_b"]), P("2",  S["td"]), P("Live Groq API call to llama-3.3-70b-versatile succeeds; Band platform reachable",      S["td"])],
        [P("10. SDK Imports",       S["td_b"]), P("5",  S["td"]), P("Band SDK, LangGraph, LangChain all importable without errors",                        S["td"])],
        [P("TOTAL",                 S["td_b"]), P("94+",S["td"]), P("Complete critical path validation — run after every significant code change",           S["td"])],
    ]
    story.append(data_table(hdr, rows, [w1, w2, w3], S))

    story += code_block(
        "uv run python preflight.py\n\n"
        "# Clean system output:\n"
        "# PREFLIGHT SUMMARY\n"
        "# Passed  : 85\n"
        "# Warnings: 9    <- Band credential placeholders (expected pre-setup)\n"
        "# Failed  : 0\n"
        "# -> CLEAR for launch after filling Band credentials",
        S, label="PREFLIGHT OUTPUT EXAMPLE")
    return story

def build_s13(S):
    story = [PageBreak(), sec_header("13.  Hackathon Track Alignment", S)]
    story.append(P(
        "Loan Shark was designed from the ground up to address every judging criterion "
        "of Track 3: Regulated & High-Stakes Workflows.", S["body"]))

    w1, w2 = UW*0.38, UW*0.62
    hdr = [P("<b>Track 3 Requirement</b>", S["th"]), P("<b>How Loan Shark Addresses It</b>", S["th"])]
    rows = [
        [P("Human oversight at critical decision points",           S["td_b"]),
         P("Mandatory human gate before any letter is dispatched. Loan officer sees full decision context and must actively approve or override. AI cannot finalize independently.", S["td"])],
        [P("Complete audit trail for regulatory review",            S["td_b"]),
         P("Band room conversation history is the full, timestamped, immutable audit trail. Every agent output with every computed field is preserved in sequence.", S["td"])],
        [P("Compliance with domain regulations",                    S["td_b"]),
         P("Dedicated Compliance Agent applies RBI lending guidelines as a hard gate. Violations issue hard blocks that override positive risk/credit scores.", S["td"])],
        [P("Structured, reproducible decision-making",              S["td_b"]),
         P("Deterministic decision matrix in the Decision Agent. Same input conditions always produce the same decision path. Full explainability.", S["td"])],
        [P("Multi-agent coordination for complex workflows",        S["td_b"]),
         P("9 specialized agents via Band @mention — each with a single, well-defined responsibility and full accountability for its output.", S["td"])],
        [P("Error handling and graceful degradation",               S["td_b"]),
         P("INTAKE_ERROR: halts pipeline on bad data. Each agent validates its own input before processing. Pipeline never proceeds with corrupt data.", S["td"])],
        [P("Deep integration with Band SDK",                        S["td_b"]),
         P("Band SDK is the only coordination mechanism. @mention is the sole inter-agent protocol. Band REST API posts the initial trigger. WebSocket maintains persistent agent connections. Remove Band — the pipeline collapses entirely.", S["td"])],
    ]
    story.append(data_table(hdr, rows, [w1, w2], S))
    return story

def build_s14(S):
    story = [PageBreak(), sec_header("14.  Future Roadmap", S)]

    story.append(P("Short Term (Post-Hackathon)", S["h2"]))
    short = [
        "Auto-polling: Streamlit polls Band REST API every 3 seconds to automatically display agent messages without manual paste",
        "Document upload: Allow actual PDF document uploads and use OCR to extract and verify document data",
        "Retry logic: Automatic retry with exponential backoff if any agent's LLM call fails",
        "Streamlit Cloud deployment: Production deployment with Streamlit secrets for API keys",
        "Multi-currency support: Full USD / GBP / EUR support with appropriate regulatory framework switching",
        "Agent timing display: Per-agent processing time shown in the pipeline tracker",
    ]
    for item in short:
        story.append(B(item, S))

    story.append(P("Medium Term", S["h2"]))
    mid = [
        "Bank integration API: REST endpoints for integration with existing Core Banking Systems (CBS)",
        "Applicant portal: Separate applicant-facing interface showing application status",
        "Batch processing: Queue-based processing for high-volume periods",
        "A/B testing framework: Compare decision outcomes across different model configurations",
        "Regulatory report generation: Auto-generate RBI quarterly compliance reports from Band room history",
    ]
    for item in mid:
        story.append(B(item, S))

    story.append(P("Long Term Vision", S["h2"]))
    story.append(P(
        "Loan Shark's architecture is generalisable beyond loan processing to any regulated, "
        "sequential, multi-stakeholder workflow. Insurance claims processing, KYC verification, "
        "trade compliance, and regulatory filing workflows all share the same pattern: "
        "specialized expertise at each stage, structured data handoffs, compliance gates, "
        "and mandatory human sign-off. The Band @mention protocol generalizes to any domain.",
        S["body"]))
    return story

def build_appendix_a(S):
    story = [PageBreak(), sec_header("Appendix A — Project File Structure", S)]
    story += code_block(
        "Loan_Shark/\n"
        "|\n"
        "+-- agents/\n"
        "|   +-- intake/agent.py          Agent 1: validates & structures raw application\n"
        "|   +-- document/agent.py        Agent 2: document completeness & consistency\n"
        "|   +-- credit/agent.py          Agent 3: credit profile & grade analysis\n"
        "|   +-- fraud/agent.py           Agent 4: fraud signals & identity checks\n"
        "|   +-- risk/agent.py            Agent 5: DTI, financial risk scoring, data aggregator\n"
        "|   +-- compliance/agent.py      Agent 6: RBI regulatory compliance\n"
        "|   +-- decision/agent.py        Agent 7: APPROVE / DENY / COUNTER_OFFER\n"
        "|   +-- pricing/agent.py         Agent 8: interest rate, EMI, fees, prepayment\n"
        "|   +-- communication/agent.py   Agent 9: formal sanction/rejection letter\n"
        "|\n"
        "+-- schema/\n"
        "|   +-- messages.py              Shared message tag constants\n"
        "|\n"
        "+-- .streamlit/\n"
        "|   +-- config.toml              Dark theme + server configuration\n"
        "|\n"
        "+-- app.py                       Streamlit UI: form + pipeline tracker + human gate\n"
        "+-- run_all.py                   Single-command launcher for all 9 agents\n"
        "+-- preflight.py                 94-check system validation script\n"
        "+-- generate_pdf.py              This PDF document generator\n"
        "|\n"
        "+-- agent_config.yaml            Band agent UUIDs and API keys  [GITIGNORED]\n"
        "+-- .env                         Environment variables          [GITIGNORED]\n"
        "+-- .env.example                 Environment variable template\n"
        "|\n"
        "+-- pyproject.toml               Project metadata and dependencies\n"
        "+-- requirements.txt             Streamlit Cloud deployment requirements\n"
        "+-- uv.lock                      Deterministic dependency lock file\n"
        "+-- README.md                    Project documentation\n",
        S)
    return story

def build_appendix_b(S):
    story = [PageBreak(), sec_header("Appendix B — Configuration Reference", S)]

    story.append(P(".env Variables", S["h2"]))
    w1, w2, w3 = UW*0.30, UW*0.14, UW*0.56
    hdr = [P("<b>Variable</b>", S["th"]), P("<b>Required</b>", S["th"]), P("<b>Description</b>", S["th"])]
    rows = [
        [P("GROQ_API_KEY",    S["td_b"]), P("Yes",       S["td"]), P("Groq API key from console.groq.com",                           S["td"])],
        [P("BAND_REST_URL",   S["td_b"]), P("Yes",       S["td"]), P("https://app.band.ai/  (do not modify)",                        S["td"])],
        [P("BAND_WS_URL",     S["td_b"]), P("Yes",       S["td"]), P("wss://app.band.ai/api/v1/socket/websocket  (do not modify)",   S["td"])],
        [P("BAND_ROOM_ID",    S["td_b"]), P("Yes*",      S["td"]), P("Room ID from band.ai room URL after creating the room",        S["td"])],
        [P("APP_ENV",         S["td_b"]), P("No",        S["td"]), P("development or production (default: development)",             S["td"])],
    ]
    story.append(data_table(hdr, rows, [w1, w2, w3], S))

    story.append(P("agent_config.yaml Structure", S["h2"]))
    story += code_block(
        "# agent_config.yaml\n"
        "# DO NOT COMMIT — this file is gitignored\n\n"
        "intake:\n"
        '  agent_id: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"\n'
        '  api_key:  "band_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"\n\n'
        "document:\n"
        '  agent_id: "..."\n'
        '  api_key:  "..."\n\n'
        "credit:\n"
        '  agent_id: "..."\n'
        '  api_key:  "..."\n\n'
        "fraud:\n"
        '  agent_id: "..."\n'
        '  api_key:  "..."\n\n'
        "# ... (repeat for: risk, compliance, decision, pricing, communication)", S)
    return story

def build_appendix_c(S):
    story = [PageBreak(), sec_header("Appendix C — API Message Reference", S)]
    story.append(P("Complete Message Tag Glossary", S["h2"]))

    tags = [
        ("NEW_LOAN_APPLICATION:",
         "Initiating message from Streamlit UI to Intake Agent. Contains raw form data as plain "
         "text — not a JSON payload. Parsed by the Intake Agent from the natural language format."),
        ("LOAN_APPLICATION:",
         "Intake Agent to Document Agent. Contains fully structured, validated LoanApplication JSON. "
         "application_id is assigned here. This is the first properly structured JSON in the chain."),
        ("DOC_VERIFICATION:",
         "Document Agent to Credit Agent. Adds doc_verdict (COMPLETE/PARTIAL/INSUFFICIENT), "
         "doc_flags[] array of specific issues found, and doc_completeness_score (0-100)."),
        ("CREDIT_ANALYSIS:",
         "Credit Agent to Fraud Agent. Adds credit_grade (A+/A/B/C/D/F), credit_tier "
         "(Prime/Near-Prime/Subprime/etc.), max_lti (maximum loan-to-income ratio), "
         "credit_behavior_notes (first-time borrower flag, utilization assessment)."),
        ("FRAUD_REPORT:",
         "Fraud Agent to Risk Agent. Adds fraud_risk_level (LOW/MEDIUM/HIGH/CRITICAL), "
         "fraud_flags[] array with flag codes and human-readable reasoning, fraud_confidence "
         "(confidence score of the fraud assessment 0-100)."),
        ("RISK_ASSESSMENT:",
         "Risk Agent to Compliance Agent. Adds risk_score (0-100), risk_category "
         "(LOW/MEDIUM/HIGH/CRITICAL), dti_before, dti_after, employment_risk_score, "
         "collateral_coverage_ratio. ALSO re-carries ALL fields from agents 1-4 to ensure "
         "Compliance Agent has complete context."),
        ("COMPLIANCE_CHECK:",
         "Compliance Agent to Decision Agent. Adds compliance_verdict "
         "(COMPLIANT/NON_COMPLIANT/CONDITIONAL), violations[] array listing any breached "
         "guidelines with specific RBI regulatory references, regulatory_notes."),
        ("LOAN_DECISION_READY:",
         "Decision Agent to Pricing Agent. Adds recommendation (APPROVE/DENY/COUNTER_OFFER), "
         "approved_amount, approved_tenure_months, decision_basis (which rule triggered), "
         "confidence (0-100%), compliance_notes (full audit note for regulatory records)."),
        ("PRICING_TERMS:",
         "Pricing Agent to Communication Agent. Adds interest_rate (percentage), "
         "processing_fee_pct, final_emi (monthly amount), prepayment_penalty (structure), "
         "insurance_premium (if applicable)."),
        ("FORMAL_LETTER_READY:",
         "Communication Agent to Human Gate (Streamlit). Adds letter_type "
         "(SANCTION_LETTER/REGRET_LETTER), letter_body (complete, formatted formal letter "
         "text ready for officer review and applicant dispatch), recommendation (carried forward)."),
        ("INTAKE_ERROR:",
         "Intake Agent to Human/System. Posted when input validation fails. Contains error_code "
         "and error_detail explaining what data was missing or invalid. HALTS the pipeline "
         "immediately — no subsequent agents are triggered."),
    ]
    for tag, desc in tags:
        story.append(KeepTogether([
            P(f"<b>{tag}</b>", S["h4"]),
            P(desc, S["body"]),
            SP(0.1),
        ]))
    return story

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    S = styles()

    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=A4,
        leftMargin=LM, rightMargin=RM,
        topMargin=TM, bottomMargin=BM,
        title="Loan Shark — Complete Project Documentation",
        author="TrenCoders",
        subject="Band of Agents Hackathon 2026 — Track 3",
    )

    story = []
    story += build_cover(S)
    story += build_toc(S)
    story += build_s1(S)
    story += build_s2(S)
    story += build_s3(S)
    story += build_s4(S)
    story += build_s5(S)
    story += build_s6(S)
    story += build_s7(S)
    story += build_s8(S)
    story += build_s9(S)
    story += build_s10(S)
    story += build_s11(S)
    story += build_s12(S)
    story += build_s13(S)
    story += build_s14(S)
    story += build_appendix_a(S)
    story += build_appendix_b(S)
    story += build_appendix_c(S)

    doc.build(story, onFirstPage=draw_cover, onLaterPages=draw_page)

    size = os.path.getsize(OUTPUT)
    print(f"\n  PDF generated successfully!")
    print(f"  Location: {OUTPUT}")
    print(f"  Size:     {size:,} bytes  ({size/1024:.1f} KB)\n")

if __name__ == "__main__":
    main()

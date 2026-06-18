# 🦈 Loan Shark — 3-Minute Demo Script & Video Shot List
## Band of Agents Hackathon 2026 · Track 3 (Regulated & High-Stakes Workflows)

This document provides a structured guide for presenting **Loan Shark** to the hackathon judges. It includes the live demo script, key visual highlights, and a video shot list for the 3-minute submission video.

---

## 🎬 Part 1: Demo Setup & Prerequisites

Before starting your recording or live pitch, configure the application state:

1. **Launch the Agent Swarm and Dashboard:**
   Ensure the Streamlit app and the background agents are running:
   ```bash
   # Terminal 1: Run all 9 agents
   uv run python run_all.py

   # Terminal 2: Run Streamlit dashboard
   uv run streamlit run app.py
   ```
2. **Demo-safe Mode (Recommended for Live Presenting):**
   - Toggle **ON** the `"Demo-safe Mode (Simulated Replay)"` checkbox in the sidebar.
   - This ensures the UI runs on a predictable ~1.2s timer, showing thoughts and transitions without waiting for external API latency or Groq rate limits.
   - For a real-time live execution over the Band API, toggle it **OFF** (requires active Band API keys configured in `.env` and `agent_config.yaml`).

---

## 🎙️ Part 2: The 3-Minute Presentation Script

### ⏱️ 0:00 - 0:30 | Hook & Problem Statement
* **Visual:** Streamlit Dashboard loaded on screen, showing the empty 9-agent pipeline card layout and the Quick Demo Scenarios panel.
* **Script:**
  > "Lending is one of the highest-stakes domains in financial services. Yet today, loan approvals still take anywhere from 3 to 14 days. Applications bounce between departments via manual email threads, creating compliance gaps, inconsistent decisions, and undocumented outcomes.
  >
  > We built **Loan Shark**: a 9-agent AI pipeline for automated, compliant, and auditable loan processing. In Loan Shark, Band's real-time messaging room *is* the immutable compliance audit trail, RBI regulations are a hard gate no AI can override, and every final decision remains under mandatory human oversight. AI advises; humans decide; Band records everything."

### ⏱️ 0:30 - 1:15 | Walkthrough 1: The Good Applicant (APPROVE)
* **Visual:** Click the **"✅ Good Applicant (Priya Sharma)"** quick fill button. Point out the auto-filled details, then click **"Submit Application"**. Watch the 9 pipeline cards light up in sequence.
* **Script:**
  > "Let's submit our first scenario: Priya Sharma, a salaried employee requesting an 8 Lakh home loan with a CIBIL score of 768. 
  > 
  > As we submit, notice the 9 pipeline stages lighting up in real time. We see the Intake Agent validation, Document verification, and Credit analysis mapping the score to Grade A. Next, the Fraud Agent scans for signals, the Risk Agent calculates the debt-to-income ratio at 15.6%, and the Compliance Agent validates it against RBI exposure limits. Finally, the Decision, Pricing, and Communication agents formulate the sanction letter. 
  > 
  > The entire multi-agent coordination is driven by Band `@mentions` in a single shared chat room. Because all 9 agents write to the same chat history, the conversation transcript becomes our official audit log."

### ⏱️ 1:15 - 2:00 | Walkthrough 2: The Human Gate & Audit Trail
* **Visual:** Scroll down to the **"🔐 Human Loan Officer Review"** section which just appeared. Point to the "Officer Name" input and checkboxes. Expand the **"📋 Compliance Audit Trail"** and click **Download PDF**.
* **Script:**
  > "Crucially, the pipeline does *not* auto-approve. It halts at the **Human Gate** (Track 3 compliance). 
  >
  > The Approve button is disabled. I must enter my name as the Officer, e.g., 'Navnit Nair', and verify the compliance checklist. Once checked, I click **Approve & Finalize**. The finalized action is timestamped and appended to the ledger.
  > 
  > Down here, a regulator can open the **Compliance Audit Trail**. It displays a structured log of all agent thoughts, key decision metrics, and lets us instantly download the record. Let's export the **Audit PDF**—a formatted, RBI-ready compliance report detailing the exact path of the application."

### ⏱️ 2:00 - 2:40 | Walkthrough 3: High Risk (DENY) & Borderline (Override)
* **Visual:** Reset and select **"❌ High Risk (Ravi Kumar)"**, then submit. Watch the pipeline halt. Show the DENY decision and compliance notes.
* **Script:**
  > "What about a high-risk applicant? Let's load Ravi Kumar—unemployed, with no credit history and no collateral. 
  >
  > As the pipeline processes, the Compliance Agent detects critical rule violations and issues a hard compliance block. The Decision Agent outputs a recommendation to **DENY**. In our design, the AI *cannot* override compliance. 
  > 
  > However, a human officer holds the ultimate authority. If a manual policy exception is warranted, the officer can choose to **Reject / Override** the AI's decision. The system forces them to document a detailed override reason before submission, logging the officer's name, timestamp, and justification into the immutable audit record."

### ⏱️ 2:40 - 3:00 | Summary & Conclusion
* **Visual:** Hover over the download buttons and show the clean sidebar.
* **Script:**
  > "By combining Band's real-time messaging, LangGraph's stateful execution, and a strict compliance-first UI, Loan Shark turns a multi-day process into a 90-second, fully audited pipeline. 
  > 
  > It is fast, consistent, regulatory-compliant, and keeps the human firmly in control. Thank you."

---

## 📹 Part 3: Video Shot List (3-Minute Submission)

| Scene | Duration | Audio / Voiceover | Video Action |
|---|---|---|---|
| **1. Intro Slide** | 0:00 - 0:15 | Intro to Loan Shark, Track 3 objectives, Team TrenCoders | Title slide or fullscreen webcam pitch. |
| **2. Problem & Solution** | 0:15 - 0:35 | Explain the manual process bottlenecks and Band's role | Screen capture showing the running dashboard in its idle state. |
| **3. Good Scenario** | 0:35 - 1:10 | Watch 9 agents process the app live; point out cards | Click "Good Applicant", click Submit, record the cards lighting up and thoughts appearing. |
| **4. Human Sign-off** | 1:10 - 1:40 | Explain officer attribution, checklist, and PDF export | Fill in "Officer Name", check boxes, click Approve, open expanded audit panel, download and open the generated PDF. |
| **5. High-Risk / Reject** | 1:40 - 2:15 | Watch compliance block the loan; show human override reason requirement | Submit "High Risk", show DENY status, enter name, click "Reject/Override", show required text area, write reason, confirm. |
| **6. Borderline / Counter** | 2:15 - 2:45 | Show COUNTER_OFFER terms adjustment in action | Submit "Borderline", show numerical inputs for amount/tenure, adjust them, complete and verify adjusted numbers in audit log. |
| **7. Outro & Call to Action** | 2:45 - 3:00 | Wrap up on how Band solved Track 3's requirements | Show final compliance dashboard or developer credits. |

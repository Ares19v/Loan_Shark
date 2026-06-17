# Spec T12 — Streamlit Cloud Deployment  (P2, bonus)

> **Owner:** Teammate (Gemini Antigravity). **Files:** `requirements.txt`, `.streamlit/`, README deploy section.
> Only start this if P1 is done. Many hackathons want a live URL — this provides it. Follow `AGENTS.md` + `GEMINI.md`.

## 1. Objective
Deploy the Streamlit UI to **Streamlit Community Cloud** so judges get a clickable live URL, with secrets handled safely.

## 2. Important scoping note
The **9 agents run as long-lived processes** (`run_all.py`) and cannot run on Streamlit Cloud. So the deployed app is the **UI**, which talks to a Band room whose agents are hosted elsewhere (a teammate's machine via `run_all.py`, or Band-hosted agents). For a self-contained public demo, ship with **Demo-safe mode** (see `spec_demo_and_pitch.md`) ON by default on the deployed URL, and document how to point it at a live room. Make this explicit in the README.

## 3. Acceptance Criteria
- [ ] `requirements.txt` matches `pyproject.toml` deps (streamlit, requests, python-dotenv, pyyaml, langchain-openai, langgraph, band-sdk[langgraph], reportlab, pypdf if used). Pin versions where it matters.
- [ ] App reads secrets from **`st.secrets`** when present, falling back to `os.getenv` for local `.env` — no secret ever hardcoded or committed.
- [ ] Deployed app loads without crashing when Band creds are absent (Demo-safe mode works with zero secrets).
- [ ] README has a "Deploy" section: how to connect the GitHub repo to Streamlit Cloud, what to put in the Secrets box (`GROQ_API_KEY`, `BAND_HUMAN_API_KEY`, `BAND_CHAT_ID`, intake handle), and the limitation about agents.
- [ ] A working public URL is captured for the submission.

## 4. Implementation Notes
- Add a tiny helper: `def secret(key, default=""): return st.secrets.get(key, os.getenv(key, default))` and route credential reads through it.
- Keep `.streamlit/config.toml` (theme). Add `.streamlit/secrets.toml` to `.gitignore` (never commit it).
- Don't change app logic beyond secret-loading + the deploy docs.

## 5. Constraints
- Never commit secrets (`secrets.toml`, `.env`, `agent_config.yaml` stay gitignored).
- Type hints + f-strings; no bare `except`.

## 6. Out of Scope
- Hosting the 9 agents in the cloud (out of scope for the deadline).
- Custom domain / auth.

## 7. Verification
- Push; connect repo on share.streamlit.io; set secrets; confirm the URL loads and Demo-safe mode runs all 3 scenarios.
- Confirm no secret is in the repo (`git log -p` / scan).
- `uv run python preflight.py` → 0 FAIL locally. Put the live URL in the README + submission.

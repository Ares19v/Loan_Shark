# Spec T11 — Document Upload → Document Agent  (P2, bonus)

> **Owner:** Teammate (Gemini Antigravity). **File:** `app.py` (form section) + the kickoff message builder.
> Only start this if your P1 task is done and verified. Follow `AGENTS.md` + `GEMINI.md`.

## 1. Objective
Let applicants **upload real documents** (ID, salary slips, ITR, bank statements) so the Document Agent's verification reflects what was actually provided — closing the "document verification is pure inference" gap a regulated-workflow judge will probe.

## 2. User Stories
- As an **applicant**, I can attach my documents in the form.
- As the **Document Agent**, I'm told which document types were actually provided, so completeness scoring is grounded in reality.
- As a **judge**, I see the system handles real artifacts, not just form fields.

## 3. Acceptance Criteria
- [ ] The form has a multi-file uploader (`st.file_uploader(accept_multiple_files=True)`, types: pdf/png/jpg) plus a small set of "document type" checkboxes (Salary slip, ITR, Bank statement, Govt ID, Business reg, GST).
- [ ] On submit, the **provided document types** (and filenames) are appended to the kickoff message in a clearly structured `DOCUMENTS_PROVIDED:` line so the Document Agent can use them.
- [ ] Uploaded files are saved to a temp dir (`tempfile`/`pathlib`); no large files committed; nothing leaves the machine beyond the kickoff text.
- [ ] If no documents are uploaded, behavior is unchanged (the agent treats them as missing, as today).
- [ ] (Optional) Lightweight text peek for PDFs via `pypdf` to include a one-line note — only if trivial; not required.

## 4. Implementation Notes
- Extend `build_application_message(form_data)` to include a `documents_provided` field, OR append a `DOCUMENTS_PROVIDED: [...]` block — coordinate with the Band-integration owner on the exact kickoff string so the `@IntakeAgent` mention stays first.
- The Document Agent prompt already lists required docs per employment type — passing the provided set lets it compute real gaps. You may add one sentence to `agents/document/agent.py`'s prompt acknowledging `DOCUMENTS_PROVIDED:` **only if** approved by the agent owner (otherwise just pass the data; the LLM will use it).
- Use `pathlib` + `tempfile`. Type hints + f-strings.

## 5. Constraints
- No real PII leaves the machine; this is a demo. Don't commit uploaded files (add the temp dir to `.gitignore` if needed).
- Don't break the kickoff `@mention` or message tags.
- Don't add heavy OCR deps (no tesseract). `pypdf` text-peek only if effortless.

## 6. Out of Scope
- Real OCR / document forgery detection.
- Storage/persistence beyond the session temp dir.

## 7. Verification
- `uv run streamlit run app.py`; upload 2 files + tick types; submit; confirm the kickoff message contains the provided-docs info (inspect the feed / demo-safe replay).
- Confirm no-upload path still works.
- `uv run python preflight.py` → 0 FAIL. Screenshot into the Walkthrough.

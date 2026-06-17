# Teammate Guide — Building Loan Shark with Gemini Antigravity

> **For teammates using Google Gemini Antigravity.**
> This guide shows you *exactly* how to turn a spec in `docs/specs/` into working, committed code.
> Read [`00_MASTER_PLAN.md`](00_MASTER_PLAN.md) first to know which task is yours.

---

## 1. One-time setup (10 minutes)

1. **Install Antigravity** from [antigravity.google](https://antigravity.google) (macOS/Windows/Linux). Sign in with your Google account. It's free in public preview.
2. **Get the repo:**
   ```bash
   git clone https://github.com/Ares19v/Loan_Shark.git
   cd Loan_Shark
   git pull origin main      # make sure you have the latest docs + specs
   ```
3. **Open the folder in Antigravity.** It will automatically read `AGENTS.md` and `GEMINI.md` at the repo root — those are your standing rules; you don't need to paste them.
4. **Install Python deps** (so the agent can run + verify):
   ```bash
   pip install uv
   uv sync
   ```
5. **Pick your task** from the Task Board in `00_MASTER_PLAN.md`. Open its spec in `docs/specs/`.

---

## 2. The golden workflow (do this for every task)

Antigravity works best **spec-first** — you hand it a complete spec, it plans, you approve, it builds and verifies. Don't drip-feed instructions.

### Step 1 — Open the Agent Manager and start a task
In the Manager surface, start a new agent task **in Planning mode** (not Fast mode) for anything non-trivial.

### Step 2 — Paste your spec as the prompt
Open your `docs/specs/spec_*.md`, copy the **whole file**, and paste it as the task prompt. Add one line at the top:

> "Implement this spec in the Loan Shark repo. Follow AGENTS.md and GEMINI.md. Work only within the scope in this spec. Produce an Implementation Plan first for my review."

### Step 3 — Review the Implementation Plan artifact
Antigravity generates an **Implementation Plan** (like a Google Doc you can comment on). **Check it against the spec's Acceptance Criteria before approving:**
- Does it touch only the files the spec allows? (If it wants to edit `band_client.py`, the agents, or the message protocol → ❌ reject, that's out of scope.)
- Does it cover every Acceptance Criterion?
- Comment inline to correct it, then approve.

### Step 4 — Let it execute, then verify in the browser
After it writes code, have it **run the app and verify visually** (Antigravity drives Chrome and takes screenshots):
```bash
uv run streamlit run app.py
```
Tell the agent: "Run the app, exercise the Verification Steps in the spec, and attach screenshots to the Walkthrough." For UI work this is your proof it actually works.

### Step 5 — Run preflight + commit
```bash
uv run python preflight.py
```
Fix any FAILs. Then commit in small atomic commits:
```bash
git add <your files>
git commit -m "feat: <what you built> (T#)"
git pull --rebase origin main      # get others' work first
git push origin main
```

---

## 3. Planning mode vs Fast mode

| Use **Planning mode** when… | Use **Fast mode** when… |
|---|---|
| Multi-file or >50 lines | A tiny, obvious one-spot edit |
| Anything in your spec | Fixing a typo / a label |
| You want to review before it runs | You're confident and it's trivial |

Default to **Planning mode** for your task. It costs a bit more but stops the agent from going off-script.

---

## 4. The prompt template (if you ever prompt outside a spec)

```markdown
# Task: <one-line objective>
Repo: Loan Shark. Follow AGENTS.md + GEMINI.md. Stay within the scope below.

## Acceptance Criteria
- [ ] <specific, testable>
- [ ] <specific, testable>

## Files I expect you to touch
- <path> (and nothing else without asking)

## Out of scope
- band_client.py, agents/*, the message protocol/tags

## Verify
- Run `uv run streamlit run app.py`, do <X>, screenshot <Y>.
- Run `uv run python preflight.py` → 0 FAIL.
Produce an Implementation Plan first.
```

---

## 5. Avoiding merge conflicts (important — multiple people edit `app.py`)

`app.py` is shared. To stay out of each other's way:
- Build your feature as a **self-contained function** the spec names (e.g. `render_audit_panel(messages)`, `render_human_gate(...)`), defined in a clearly marked section. The integration owner wires the single call site.
- **Always `git pull --rebase origin main` before you push.** Commit small and often (Antigravity agents sometimes terminate mid-task — frequent commits = little lost work).
- If your spec says a piece is owned by the core integration workstream (Band client, agents, parsing), **do not touch it** — request the change in the master plan instead.

---

## 6. Known Antigravity gotchas (June 2026)

- **"Agent execution terminated"** mid-task happens — just resume; your committed work is safe. Keep tasks small.
- **"Generating…" hangs** can mean a model quota lockout — switch model (Gemini 3 Pro ↔ Flash) and retry.
- **Prompt injection** — don't paste untrusted external content into a task; stick to our specs.
- Keep each task **atomic** (one spec, one feature). Don't ask one agent to do T6 + T7 + T8 together.

---

## 7. Definition of done for a teammate task

- [ ] Every Acceptance Criterion in your spec is met.
- [ ] Verified live in the browser with screenshots in the Walkthrough.
- [ ] `preflight.py` → 0 FAIL.
- [ ] No secrets committed; you stayed in scope.
- [ ] Small, clear commits pushed to `main`; you rebased first.
- [ ] You ticked your task box in `00_MASTER_PLAN.md`.

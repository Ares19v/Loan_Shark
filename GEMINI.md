# GEMINI.md — Antigravity-Specific Rules for Loan Shark

> **Antigravity reads this file and it takes precedence over `AGENTS.md` when they conflict.**
> Everything in `AGENTS.md` still applies — this file only adds Antigravity-specific behavior.

---

## Start here, every session

1. Read **`AGENTS.md`** (project rules, tech stack, the message protocol, guardrails).
2. Read **`docs/00_MASTER_PLAN.md`** (objectives + the task board with priorities and owners).
3. Find your assigned task spec in **`docs/specs/`** and read it fully before acting.
4. Read **`docs/02_TEAMMATE_GUIDE_ANTIGRAVITY.md`** if this is your first time — it shows exactly how to run a spec here.

## How to work in Antigravity on this repo

- **Use Planning mode for any task that touches more than ~50 lines or more than one file.** Review the generated *Implementation Plan* artifact and make sure it matches the spec's Acceptance Criteria before you let it execute. Use Fast mode only for tiny, obvious edits.
- **Paste the whole task spec** (`docs/specs/spec_*.md`) as your prompt. The specs are written in the format Antigravity follows best (Objective → User Stories → Acceptance Criteria → Data Flow → Constraints → Out-of-Scope → Verification).
- **Verify UI changes in the browser.** When you change `app.py`, run the app and use Antigravity's browser + screenshot to confirm the form, the 9-card tracker, and the Human Gate render and behave correctly. Attach screenshots to your Walkthrough.
- **Commit often, in small atomic commits.** Antigravity agents sometimes terminate mid-task — frequent commits mean you never lose much. Use `feat:` / `fix:` / `docs:` prefixes.
- **Stay inside your spec's scope.** Each spec lists Out-of-Scope items. Do not refactor `band_client.py`, the agents, or the message protocol — those are owned by the Claude Code workstream. If a spec needs a change there, flag it in the master plan instead.

## Hard guardrails (repeat of the critical ones)

- Do **not** commit `.env`, `agent_config.yaml`, or any API key.
- Do **not** remove or bypass the Human Gate.
- Do **not** rename message tags or `@mention` handles (see `AGENTS.md` §3).
- Keep the 3 demo scenarios working (Good/Borderline/High Risk).
- Run `uv run python preflight.py` before you consider a task done.

## Model suggestion

Gemini 3 Pro (Planning mode) for design + multi-file work; Gemini 3 Flash for quick edits. Claude Sonnet inside Antigravity is a good second opinion for tricky typed-Python logic.

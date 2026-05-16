---
name: run-workstream-task
description: >
  Execute one bounded task from a Rust workstream TODO.md. Use when a task ID is ready, when setting
  a Codex goal for a single task, or when delegating implementation/debug work to tdd or diagnose
  while preserving task ledger, evidence, journal, and handoff updates.
---

# Run Workstream Task

Own one task. Do not rewrite the whole workstream.

## Inputs

Require or infer:

- workstream path,
- task ID from `TODO.md`,
- file/module scope,
- dependencies,
- validation command,
- whether this is feature work or diagnosis.

If any of these are missing, read `TODO.md`, `WORKSTREAM.json`, and `HANDOFF.md`. If still unclear,
stop and ask the planner to refine the task.

## Route Execution

- Feature or behavior slice -> invoke `tdd`.
- Bug, failing test, flake, or performance regression -> invoke `diagnose`.
- Unfamiliar code blocks progress -> invoke `zoom-out`, then resume.

Pass the delegated skill:

- task ID,
- file scope,
- validation command,
- relevant ADR/workstream paths,
- and expected evidence update.

## During Work

- Stay inside the assigned scope unless the task proves wrong.
- Do not revert user or other worker changes.
- Prefer targeted `cargo nextest run` during iteration.
- Update only this task's status and notes unless acting as planner.

## Finish

Update:

- task status in `TODO.md`,
- evidence notes in `EVIDENCE_AND_GATES.md` when a gate is added or proven,
- `HANDOFF.md` if another agent may continue,
- `JOURNAL/YYYY-MM-DD-<task-id>.md` for session details when useful.

Report changed files, validation, blockers, and next recommended action.

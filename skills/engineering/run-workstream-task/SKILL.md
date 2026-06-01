---
name: run-workstream-task
description: >
  Executes one bounded task from a Rust workstream TODO.md. Use when a task ID is ready, when setting
  a Codex goal for a single task, or when delegating implementation/debug work to tdd or diagnose
  while preserving task ledger, evidence, journal, and handoff updates.
---

# Run Workstream Task

Own one task. Do not rewrite the whole workstream.

## Inputs

Require or infer:

- workstream path,
- task ID from `TODO.md`,
- matching task object from `TASKS.jsonl` when present,
- approved campaign or bundle from `CAMPAIGNS.jsonl` when this task is auto-advanced,
- file/module scope,
- required context files or `CONTEXT.jsonl` entries,
- dependencies,
- validation command,
- whether this is feature work or diagnosis.

If any of these are missing, read `TODO.md`, `WORKSTREAM.json`, `CONTEXT.jsonl` when present, and
`HANDOFF.md`. If still unclear, stop and ask the planner to refine the task.
Use `../dev-flow/references/artifact-contracts.md` to resolve task-ledger drift and
`../dev-flow/references/worktree-safety.md` before edits in a linked worktree.

## Route Execution

- Feature or behavior slice -> invoke `tdd`.
- Bug, failing test, flake, or performance regression -> invoke `diagnose`.
- Unfamiliar code blocks progress -> invoke `zoom-out`, then resume.

Pass the delegated skill:

- task ID,
- file scope,
- validation command,
- relevant ADR/workstream/context paths,
- and expected evidence update.

## During Work

- Stay inside the assigned scope unless the task proves wrong.
- Read required context before editing. If it is missing, stale, or contradictory, return
  `NEEDS_CONTEXT`.
- Do not revert user or other worker changes.
- Prefer targeted `cargo nextest run` during iteration.
- Update only this task's status and notes unless acting as planner.
- Propose follow-up or split tasks in the final report instead of changing the workstream target
  state or global priority.
- Use task-local validation evidence before reporting `DONE`; final acceptance remains with the
  planner/reviewer after review and fresh verification.

## Example

```text
Use $run-workstream-task to execute task EMU-020 from docs/workstreams/emulator-mvp/TODO.md.
```

## Finish

Update:

- task status in `TODO.md`,
- evidence notes in `EVIDENCE_AND_GATES.md` when a gate is added or proven,
- `HANDOFF.md` if another agent may continue,
- `JOURNAL/YYYY-MM-DD-<task-id>.md` for session details when useful.

Final status must be one of:

- `DONE`: implementation and task-local validation completed.
- `DONE_WITH_CONCERNS`: completed, but named concerns need planner or reviewer attention.
- `BLOCKED`: cannot finish without task split, design change, or external input.
- `NEEDS_CONTEXT`: missing information prevents safe execution.

Report a structured handoff block with status, changed files, validation, evidence updates,
blockers, concerns, review/verify readiness, a one-paragraph planner summary, and an advisory
same-lane next action if accepted. The next action is advisory unless the planner pre-approved
same-lane continuation. End by telling the user to return the report to the integrator for review,
verification, and the next approved task or bundle.
Include the `WORKSTREAM_RESULT:` marker from `../dev-flow/references/agent-contracts.md`.

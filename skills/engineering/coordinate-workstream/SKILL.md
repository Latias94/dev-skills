---
name: coordinate-workstream
description: >
  Coordinates an active Rust workstream across planner, worker, reviewer, and docs terminals. Use
  when running multiple Codex terminals, assigning tasks, integrating worker handoffs, reviewing
  evidence, resolving scope conflicts, or deciding whether to continue, close, or split follow-on
  work.
---

# Coordinate Workstream

Use this from the planner / PM terminal. Do not implement worker tasks here.

## Read First

Read only what is needed:

- `WORKSTREAM.json`
- `TODO.md`
- `HANDOFF.md`
- `EVIDENCE_AND_GATES.md`
- latest relevant `JOURNAL/*.md`
- git status and active branches/worktrees

If there is no active workstream, return to `dev-flow` and open or resume one first.

## Terminal Roles

- **Planner / PM**: owns decomposition, task ledger, sequencing, conflicts, and closeout.
- **Worker**: owns one bounded `TODO.md` task with explicit file scope and validation.
- **Reviewer**: checks worker output against repo rules, workstream intent, and gates.
- **Docs / next-version**: explores future requirements, PRDs, ADR candidates, or prototypes.

Docs terminals must not redefine the active workstream target or rewrite the current task ledger
without planner approval.

## Coordination Loop

1. Confirm the active lane target, gates, and unfinished tasks.
2. Choose which tasks are ready, blocked, or unsafe to parallelize.
3. Assign each worker one task ID, owner, file/module scope, dependencies, and validation command.
4. Tell workers to use `run-workstream-task`; it will delegate to `tdd` or `diagnose`.
5. Integrate worker reports: changed files, validation, evidence, blockers, and handoff notes.
6. Update only planner-owned state: task order, owner assignment, conflict notes, and next action.
7. Decide whether to run another task, request review, close the lane, split a follow-on, or handoff.

## Guardrails

- Do not parallelize overlapping file scopes unless explicitly serialized.
- Do not assign work without an independently runnable validation command.
- Use Codex goals only for one bounded task from `TODO.md`.
- Stop and revisit planning when a worker discovers the task changes an ADR or target state.
- Promote durable decisions from chat or journal into ADRs or workstream docs.

## Example

```text
Use $coordinate-workstream to coordinate docs/workstreams/emulator-mvp across planner, backend worker,
frontend worker, reviewer, and next-version docs terminals.
```

## Output

Report:

- active workstream path,
- terminal role map,
- ready worker assignments,
- blocked or unsafe tasks,
- conflicts to resolve,
- evidence/review status,
- and next planner action.

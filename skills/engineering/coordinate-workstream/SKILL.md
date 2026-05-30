---
name: coordinate-workstream
description: >
  Coordinates Rust workstreams or architecture lanes across planner, lane, worker, reviewer, and
  docs terminals. Use when discovering which workstreams are active, planning terminal/worktree
  layout, assigning tasks, integrating handoffs, reviewing evidence, resolving scope conflicts,
  syncing branches, or deciding whether to continue, close, or split follow-on work.
---

# Coordinate Workstream

Use this from the planner / PM terminal. The planner can be a separate terminal or the user's main
control terminal. Do not implement worker tasks here.

## Read First

If the user names a workstream or lane, read only what is needed:

- `WORKSTREAM.json`
- `docs/architecture/LANES.md` or referenced architecture maps when present
- `TODO.md`
- `HANDOFF.md`
- `EVIDENCE_AND_GATES.md`
- latest relevant `JOURNAL/*.md`
- git status and active branches/worktrees

If the user does not name a target, discover candidates first:

- `docs/architecture/LANES.md`, `WORKSTREAM_LINKS.md`, and architecture maps
- `docs/workstreams/*/WORKSTREAM.json`
- git status, `git worktree list`, active branches, and related repo hints
- for large workstream dirs, run `scripts/workstream_inventory.py --root <repo>` first

Do not assume a "current workstream". If no obvious target exists, report candidate workstreams,
candidate lanes, and a recommended terminal plan instead of assigning work. If there is no active
workstream and no architecture lane registry, return to `audit-project-scale` or `dev-flow` first.

## Terminal Roles

- **Planner / PM**: owns decomposition, task ledger, sequencing, conflicts, and closeout.
- **Architecture Lane**: owns one capability area across queued workstreams and reports shared-scope
  conflicts to the planner.
- **Worker**: owns one bounded `TODO.md` task with explicit file scope and validation.
- **Reviewer**: checks worker output against repo rules, workstream intent, and gates.
- **Docs / next-version**: explores future requirements, PRDs, ADR candidates, or prototypes.

Docs terminals must not redefine the active workstream target or rewrite the current task ledger
without planner approval.

## Coordination Loop

Before assigning terminals:

1. Identify active workstream or architecture-lane candidates.
2. Recommend planner, lane, worker, reviewer, and docs terminals only where useful.
3. Include path/branch/worktree/repo assumptions, sync blockers, and `references/planner-state.md`.

For one active workstream:

1. Confirm the active lane target, gates, and unfinished tasks.
2. Choose which tasks are ready, blocked, or unsafe to parallelize.
3. Assign each worker one task ID, owner, file/module scope, dependencies, and validation command.
4. Tell workers to use `run-workstream-task`; it will delegate to `tdd` or `diagnose`.
5. Integrate worker reports: changed files, validation, evidence, blockers, and handoff notes.
6. Require worker status: `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, or `NEEDS_CONTEXT`.
7. Send completed work to `review-workstream` before accepting it into the lane.
8. Use `verify-rust-workstream` before marking task, goal, or lane completion.
9. Update only planner-owned state: task order, owner assignment, conflict notes, and next action.
10. Decide whether to run another task, request review, close the lane, split a follow-on, or handoff.

For architecture lanes:

1. Read lane registry and active workstreams for each lane terminal.
2. Confirm owned scopes, shared scopes, dirty state, branch, and last sync point.
3. Approve which lane may continue, which must sync main, and which is blocked by shared scope.
4. Keep lane terminals on `run-architecture-lane`; do not assign raw tasks across lane boundaries.
5. Integrate completed workstreams one at a time, with review and fresh verification.

## Guardrails

- Do not parallelize overlapping file scopes unless explicitly serialized.
- Do not let lane terminals modify shared scopes without planner coordination.
- Do not assign work without an independently runnable validation command.
- Use Codex goals only for one bounded task from `TODO.md`.
- Do not treat worker-reported success as completion without review and fresh verification.
- Stop and revisit planning when a worker discovers the task changes an ADR or target state.
- Promote durable decisions from chat or journal into ADRs or workstream docs.

## Example

```text
Use $coordinate-workstream to inspect this repo, identify active workstreams or architecture lanes,
and recommend the planner/lane/worker terminal layout before assigning tasks.
```

## Output

Report active workstream candidates, architecture lane map, terminal role map, path/branch/worktree
sync status, ready assignments, blocked or unsafe tasks, conflicts, evidence/review status, worker
status summary, and next planner action.

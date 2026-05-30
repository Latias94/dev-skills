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

For selected architecture directions, delegate to `plan-architecture-lane`. For planner operations, read the relevant references: result inspection, integration protocol, side-effect approval, cross-repo coordination, worktree lifecycle, lane goal bundles, context manifests, and planner state.

## Terminal Roles

- **Planner / PM**: owns workstream creation/reuse, task ledger, lane bundles, sequencing, and closeout.
- **Architecture Lane**: owns one capability area across queued workstreams and reports shared-scope
  conflicts to the planner.
- **Worker**: owns one bounded `TODO.md` task with explicit file scope and validation.
- **Reviewer**: checks worker output against repo rules, workstream intent, and gates.
- **Docs / next-version**: explores future requirements, PRDs, ADR candidates, or prototypes.

Docs terminals must not redefine the active workstream target or rewrite the current task ledger
without planner approval.

## Coordination Loop

Before assigning terminals:

1. Identify active workstream or architecture-lane candidates; use `plan-architecture-lane` when planning depth or docs/code alignment is unclear.
2. Draft a lane goal bundle: target lane, workstream queue, one to three ready tasks, owned scopes,
   shared scopes, validation, context manifest, and stop conditions.
3. Recommend terminals/worktrees; after approval, create or hand commands to the user.
4. Include proposed commands/prompts, sync blockers, context manifest path, and planner-state
   updates.

For one active workstream:

1. Confirm lane target, gates, unfinished tasks, and ready/blocked/unsafe slices.
2. Assign each worker one task ID with owner, file scope, required context, dependencies, and
   validation command.
3. Tell workers to use `run-workstream-task`; require `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, or
   `NEEDS_CONTEXT`.
4. Integrate worker reports, then route completed work through `review-workstream` and
   `verify-rust-workstream`.
5. Update only planner-owned state and choose the next action: run another task, review, close,
   split follow-on, or handoff.

For architecture lanes:

1. Read lane registry and active workstreams for each lane terminal.
2. Confirm owned scopes, shared scopes, dirty state, branch, and last sync point.
3. Approve a lane goal bundle before asking a lane terminal to continue.
4. Approve which lane may continue, which must sync main, and which is blocked by shared scope.
5. Keep lane terminals on `run-architecture-lane`; do not assign raw tasks across lane boundaries.
6. Integrate completed workstreams one at a time, with review and fresh verification.

## Guardrails

- Prefer stable lane worktrees; do not parallelize overlapping file scopes unless serialized.
- Do not let lane terminals modify shared scopes without planner coordination.
- Do not create worktrees or assign work without approval and runnable validation.
- Use Codex goals only for one bounded task or one planner-approved lane goal bundle, never the lane.
- Do not treat worker-reported success as completion without review and fresh verification.
- Stop and revisit planning when a worker discovers the task changes an ADR or target state.
- Promote durable decisions from chat or journal into ADRs or workstream docs.

## Output
Report candidates or inspected results, lane bundles, Codex goals to set after approval, terminal prompts, approvals, cross-repo/worktree impacts, conflicts, evidence, statuses, and next action.
```text
Use $coordinate-workstream to inspect this repo and prepare a multi-terminal plan.
```

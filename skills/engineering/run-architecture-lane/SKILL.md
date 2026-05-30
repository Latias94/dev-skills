---
name: run-architecture-lane
description: >
  Runs a long-lived Rust architecture lane from one terminal or worktree. Use when a large project
  has capability areas such as storage, transcode, playback, realtime, or admin, and the user wants
  this terminal to keep advancing related workstreams instead of switching per workstream.
---

# Run Architecture Lane

Use this from an architecture-lane terminal. The terminal owns a capability area, not one task.

Do not use this for small projects, one-off bugs, or a single workstream that does not need a
long-lived terminal. Return to `audit-project-scale` or `dev-flow` for those.

## Read First

Read only what is needed:

- relevant `docs/architecture/*.md` and `WORKSTREAM_LINKS.md` if present,
- active `docs/workstreams/*/WORKSTREAM.json`,
- matching `TODO.md`, `HANDOFF.md`, and `EVIDENCE_AND_GATES.md`,
- git status, current branch, and linked worktrees.

Prefer an existing lane registry when present. If none exists, infer the lane from architecture
refs, capability tags, file scopes, and user intent.

## Lane Contract

Before execution, confirm:

- lane slug and architecture refs,
- owned file/module scopes,
- shared scopes that require planner coordination,
- active workstream or next queued workstream,
- planner-approved lane goal bundle when this terminal is meant to run for a long time,
- branch/worktree path and sync point with main,
- context manifest path, usually `docs/workstreams/<slug>/CONTEXT.jsonl`,
- validation gates and closeout expectations.

Prefer one stable worktree per architecture lane, not one worktree per workstream. Reuse the lane
worktree across queued workstreams; use branch changes only when the planner wants isolation.

A lane goal bundle is the maximum autonomous scope for this terminal. It may contain one to three
same-lane tasks or one short workstream queue, but it must have explicit stop conditions. If no
planner-approved bundle exists, pick only the next safe bounded task and ask the planner before
continuing further.

## Loop

1. Reconstruct lane state from docs and git.
2. Read the context manifest and required ADR / architecture refs before execution.
3. If no active workstream fits, delegate to `open-workstream`.
4. For the active workstream, choose the next bounded task and delegate to `run-workstream-task`.
5. Send completed slices to `review-workstream`, then `verify-rust-workstream`.
6. Update evidence, handoff, and lane state.
7. Use `close-workstream` when the current workstream reaches its gates.
8. Recommend the next same-lane task or workstream to the planner.
9. Continue only within the planner-approved lane goal bundle.
10. Sync with main before starting the next queued workstream.
11. Stop and escalate when stop conditions, shared scopes, ADR changes, schema changes, or lane
    conflicts appear.

## Guardrails

- Do not let a lane become an unlimited refactor branch.
- Do not claim global scope; shared crates require coordination.
- Do not set a Codex goal for the whole lane. If the user explicitly asks for a goal, bind it to
  the current planner-approved lane goal bundle, next bounded task, or active workstream milestone.
- Recommend same-lane next actions only. The planner owns global sequencing and cross-lane priority.
- Do not start the next workstream if the current branch is dirty, unreviewed, or unverified.
- Do not continue after `BLOCKED`, `NEEDS_CONTEXT`, failed validation, missing context files, or a
  shared-scope change. Report to the planner and wait.

## Output

Report lane slug, active workstream, current lane goal bundle, branch/worktree, context manifest,
owned and shared scopes, completed task, validation, conflicts, recommended same-lane next action,
whether a bounded Codex goal should be set next, next sync point, and a reminder to return the
report to the planner for review, verification, and the next approved bundle.

## Example

```text
Use $run-architecture-lane for the nako storage lane. Keep this terminal on the storage worktree,
advance queued storage/VFS workstreams, and stop when shared database or server contracts need
planner coordination.
```

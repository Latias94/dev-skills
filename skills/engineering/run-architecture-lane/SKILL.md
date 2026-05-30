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
- branch/worktree path and sync point with main,
- validation gates and closeout expectations.

Stable terminal path with rotating workstream branches is preferred: keep the terminal on the
architecture lane, but use short-lived branches for each workstream.

## Loop

1. Reconstruct lane state from docs and git.
2. If no active workstream fits, delegate to `open-workstream`.
3. For the active workstream, choose the next bounded task and delegate to `run-workstream-task`.
4. Send completed slices to `review-workstream`, then `verify-rust-workstream`.
5. Update evidence, handoff, and lane state.
6. Use `close-workstream` when the current workstream reaches its gates.
7. Sync with main before starting the next queued workstream.
8. Stop and escalate when shared scopes, ADR changes, schema changes, or lane conflicts appear.

## Guardrails

- Do not let a lane become an unlimited refactor branch.
- Do not claim global scope; shared crates require coordination.
- Do not set a Codex goal for the whole lane. If the user explicitly asks for a goal, bind it to
  the next bounded task or active workstream milestone.
- Do not start the next workstream if the current branch is dirty, unreviewed, or unverified.

## Output

Report lane slug, active workstream, branch/worktree, owned and shared scopes, next task, delegated
skill, validation command, conflicts, whether a bounded Codex goal is recommended, and next sync
point.

## Example

```text
Use $run-architecture-lane for the nako storage lane. Keep this terminal on the storage worktree,
advance queued storage/VFS workstreams, and stop when shared database or server contracts need
planner coordination.
```

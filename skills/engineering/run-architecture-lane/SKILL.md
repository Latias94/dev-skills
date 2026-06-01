---
name: run-architecture-lane
description: >
  Runs a long-lived Rust architecture lane from one terminal or worktree. Use when a large project
  has capability areas such as storage, transcode, playback, realtime, or admin, and the user wants
  this terminal to keep advancing related workstreams, execute approved campaigns, or propose the
  next same-lane medium goal without returning to a global planner after every task.
---

# Run Architecture Lane

Use this from an architecture-lane terminal. The terminal owns a capability area, not one task.

Do not use this for small projects, one-off bugs, or a single workstream without a long-lived
terminal. Return to `audit-project-scale` or `dev-flow` for those.

## Read First

Read only what is needed:

- relevant `docs/architecture/*.md` and `WORKSTREAM_LINKS.md` if present,
- active `docs/workstreams/*/WORKSTREAM.json`,
- matching `TODO.md`, `HANDOFF.md`, and `EVIDENCE_AND_GATES.md`,
- git status, current branch, and linked worktrees.

Prefer an existing lane registry; otherwise infer the lane from architecture refs, capability tags,
file scopes, and user intent. Use `../dev-flow/references/worktree-safety.md` for identity drift.

## Lane Contract

Before execution, confirm:

- lane slug and architecture refs,
- owned file/module scopes,
- shared scopes that require upper-planner coordination,
- active workstream or next queued workstream,
- approved lane goal bundle when this terminal is meant to run for a long time,
- branch/worktree path and sync point with main,
- context manifest plus `TASKS.jsonl` / `CAMPAIGNS.jsonl` state,
- validation gates and closeout expectations.

Prefer one stable worktree per architecture lane, not one worktree per workstream. Reuse the lane
worktree across queued workstreams; use branch changes only when the upper planner wants isolation.

A lane goal bundle or approved lane campaign is this terminal's maximum autonomous scope. Campaigns
must have ordered steps, gates, auto-advance rules, and stop conditions.
If no approved scope exists, pick one safe bounded task or prepare a next-goal proposal.

For dependency-ordered work that is not safe to parallelize, prefer an approved serial lane
campaign over stopping after every task. Auto-advance only within the approved order and gates.

## Loop

1. Reconstruct lane state from docs and git.
2. Read the context manifest, task state, campaign state, and required ADR / architecture refs before execution.
3. If no active workstream fits, delegate to `open-workstream`.
4. For the active workstream, choose the next bounded task and delegate to `run-workstream-task`.
5. Report completed slices for integration; integrator/reviewer owns acceptance through
   `review-workstream` and fresh `verify-rust-workstream`.
6. Update evidence, handoff, and lane state.
7. Use `close-workstream` when the current workstream reaches its gates.
8. If the approved campaign still has steps, auto-advance only after gates, evidence, and campaign state update pass.
9. If the campaign is complete, propose the next same-lane medium goal from lane docs, workstreams,
   code evidence, and validation readiness.
10. Continue only within the approved lane bundle or campaign, or after the user explicitly sets the
    next lane goal.
11. Sync with main before starting the next queued workstream when integration says to.
12. Stop and escalate when stop conditions, shared scopes, ADR changes, schema changes, or lane
    conflicts appear.

Use `../dev-flow/references/gate-taxonomy.md` for revision and escalation loops after review or
verification failures.

## Guardrails

- Do not let a lane become an unlimited refactor branch.
- Do not claim global scope; shared crates require coordination.
- Do not set a Codex goal for the whole lane. For ready bundles/campaigns, ask whether this
  terminal should set the bounded goal, or set it directly if already approved in this conversation.
- Recommend same-lane next goals only. The upper planner owns global sequencing and cross-lane priority.
- Do not wait for the upper planner just to discover same-lane follow-ups; propose them with scope,
  evidence, validation, and stop conditions.
- Do not start the next workstream if the current branch is dirty, unreviewed, or unverified.
- Do not continue after `BLOCKED`, `NEEDS_CONTEXT`, failed validation, missing context files, or a
  shared-scope change. Report to the upper planner or integrator and wait.

## Output

Final output must include a structured handoff block with status, lane/workstream/task,
branch/worktree, changed files, validation, evidence, concerns, review/verify readiness, and
same-lane next proposal. Use the `WORKSTREAM_RESULT:` marker from `agent-contracts.md`.

## Example

```text
Use $run-architecture-lane for the nako storage lane. Keep this terminal on the storage worktree,
advance queued storage/VFS workstreams, and stop when shared database or server contracts need
upper-planner coordination.
```

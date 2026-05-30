# Usage

Chinese documentation: [zh-CN/usage.md](./zh-CN/usage.md)

Most users should start with `$dev-flow`.

`$dev-flow` is the orchestrator. It should actively delegate to the next skill instead of only
telling the user what to do next.

Use `$audit-project-scale` first when the repo is unfamiliar, old workflow docs may be stale, or you
are deciding whether multiple terminals and architecture lanes are justified.

For large projects, use `$run-architecture-lane` when one terminal should keep owning a capability
area such as storage, transcode, playback, realtime, or admin.

## Choose By Repo Size

| Situation | Skill to call | Notes |
| --- | --- | --- |
| Small repo, one bounded change | `$dev-flow` | Let it route to `tdd` or `diagnose`; avoid heavy docs. |
| Medium repo, multi-step change | `$dev-flow` | Open or reuse one workstream when traceability matters. |
| Large repo, capability-scoped worktrees | `$audit-project-scale` first | Confirm lane boundaries before using `$run-architecture-lane`. |
| Multiple active terminals | `$coordinate-workstream` | Use a planner terminal or your main control terminal. |
| Too many workstreams | `$coordinate-workstream` | Run inventory, close stale active lanes, and keep only a short active queue. |
| Old workstream or architecture docs | `$audit-project-scale` | Repair substrate before adding new workstreams. |

## Common User Calls

Initialize a project:

```text
Use $dev-flow to initialize this Rust repo for the dev-skills workflow.
```

Audit workflow scale:

```text
Use $audit-project-scale on this Rust repo. Decide whether it should stay lightweight, use normal
workstreams, or add architecture lanes and planner coordination.
```

Plan a large feature:

```text
Use $dev-flow to plan this feature. Clarify requirements if needed, then create or reuse the right
workstream and split executable tasks.
```

Implement a bounded task:

```text
Use $dev-flow to execute task ABC-020 from docs/workstreams/<slug>/TODO.md.
```

Debug a failure:

```text
Use $dev-flow to diagnose this failing test and record regression evidence in the active workstream.
```

Prepare a handoff:

```text
Use $dev-flow to prepare a handoff for the current workstream.
```

Discover a multi-terminal plan:

```text
Use $coordinate-workstream to inspect this repo, identify active workstreams or architecture lanes,
and recommend planner, lane, worker, reviewer, and docs terminals.
```

Coordinate a known workstream:

```text
Use $coordinate-workstream to coordinate docs/workstreams/<slug> across planner, worker, reviewer,
and docs terminals.
```

Coordinate architecture lanes:

```text
Use $coordinate-workstream to coordinate architecture lanes, shared scopes, branch sync, and completed workstream integration.
```

Inventory many workstreams:

```text
Use $coordinate-workstream to inventory docs/workstreams, summarize active/draft workstreams by lane,
identify stale or missing lane metadata, and recommend which workstreams to close, keep active, or defer.
```

Run a long-lived architecture terminal:

```text
Use $run-architecture-lane for the storage lane. Keep this terminal on storage/VFS workstreams and stop when shared database or server contracts need coordination.
```

Review and verify a completed task:

```text
Use $dev-flow to review and verify task ABC-020 before marking it complete.
```

Recover a broken Codex session:

```text
Use $codex-session-recovery to recover continuation context from the latest Codex session.
```

## Direct Matt Pocock Skill Calls

Call these directly when you want that explicit action, rather than the normal development router.

Configure issue tracker/domain docs:

```text
Use $setup-matt-pocock-skills to configure AGENTS.md and docs/agents for this repo.
```

Pressure-test an idea before project docs exist:

```text
Use $grill-me to challenge this project idea until the MVP, non-goals, and risks are precise.
```

Pressure-test a plan against existing docs:

```text
Use $grill-with-docs to pressure-test this plan against CONTEXT.md, ADRs, and active workstreams.
```

Understand unfamiliar code:

```text
Use $zoom-out to explain how this subsystem fits into the larger project.
```

Review architecture:

```text
Use $improve-codebase-architecture to find crate-boundary, module-depth, and testability problems.
```

Execute architecture refactoring:

```text
Use $fearless-refactor on the top recommendation from the architecture report and route it through $dev-flow.
```

Prepare release notes:

```text
Use $changelog to update CHANGELOG.md from the latest tag to HEAD.
```

Build a throwaway experiment:

```text
Use $prototype to test two designs before we commit to an ADR.
```

Export to project tracker:

```text
Use $to-prd to turn this clarified plan into a PRD, then $to-issues if it should become GitHub issues.
```

Create a reusable skill:

```text
Use $write-a-skill to create a project-specific skill for this repeated workflow.
```

## Manual Recovery Skill

Call `$codex-session-recovery` directly after a Codex crash, context corruption,
`invalid_encrypted_content`, or when a new chat needs to reconstruct what happened in a previous
session. It reads Codex session JSONL files and returns recovery evidence; project docs and git state
still outrank recovered transcript content.

```text
Use $codex-session-recovery to read this Codex session id and reconstruct the active goal, recent tool activity, compaction summary, and safe continuation plan: 019e2779-da60
```

## Default User Experience

```text
User -> $dev-flow -> delegated skill -> $dev-flow resumes routing
```

The user should not need to remember internal workflow skills. `$dev-flow` should decide whether the
next move is bootstrap, grill, workstream planning, TDD execution, diagnosis, review, or handoff.
Use `$audit-project-scale` when the workflow scale itself is the question. `$run-architecture-lane`
is the other default entrypoint for large-project lane terminals.

Example chain:

```text
User asks for large feature
-> $dev-flow detects unclear requirements
-> delegates to $grill-with-docs
-> resumes and delegates to $open-workstream
-> creates task ledger
-> delegates multi-terminal planning to $coordinate-workstream when needed
-> delegates first task to $tdd or $diagnose
-> reviews completed work with $review-workstream
-> verifies fresh evidence with $verify-rust-workstream
-> records evidence and handoff
```

## Codex Goals

Codex goals are useful for one bounded task from a workstream task ledger.

Use goals for:

- one task ID from `TODO.md`,
- a single bug fix,
- a bounded validation loop.

Do not use goals for:

- the whole workstream,
- long-term architecture memory,
- replacing ADRs or workstream docs.

Recommended pattern:

```text
1. $open-workstream creates task ABC-020.
2. User asks Codex to set ABC-020 as the current goal.
3. Agent executes and validates the task.
4. Agent reviews the output and runs fresh verification.
5. Agent marks the goal complete only after the task is genuinely done.
6. Agent updates TODO.md and EVIDENCE_AND_GATES.md.
```

## Internal Workflow Skills

These are normally invoked by `$dev-flow`, not manually:

- `setup-rust-workstreams`
- `open-workstream`
- `coordinate-workstream`
- `resume-workstream`
- `run-workstream-task`
- `review-workstream`
- `verify-rust-workstream`
- `close-workstream`

Directly call one only when you intentionally want to bypass the router, or when the planner terminal
is actively coordinating multiple terminals with `coordinate-workstream`.

## Multi-Agent Use

Only parallelize when tasks have clear boundaries.

Planner prompt:

```text
Use $coordinate-workstream to inspect this repo and prepare a multi-terminal plan.
Do not assume a current workstream. Recommend terminals only when scopes, branches, dependencies,
and validation commands are clear.
```

For large multi-worktree work, the planner may keep local runtime state in
`.codex/planner-state.local.json`; do not commit personal absolute paths.

Worker prompt:

```text
Use $run-workstream-task to execute task ABC-020. It should delegate to $tdd or $diagnose as needed,
stay within the assigned file scope, and update the task ledger and journal when done.
```

Reviewer prompt:

```text
Use $review-workstream to review completed task ABC-020 against the workstream contract and repo
standards.
```

Verifier prompt:

```text
Use $verify-rust-workstream to verify task ABC-020 with fresh command evidence before completion.
```

Workers should not rewrite the global task ledger or redefine the workstream target state.

## Skill Delegation

When a skill hands off to another skill, it should pass the minimum durable context:

- workstream path,
- task ID,
- file scope,
- validation command,
- relevant ADR/docs,
- and expected output artifact.

Example:

```text
Delegate to $tdd:
Task: ABC-020
Workstream: docs/workstreams/<slug>
Scope: crates/foo/src/**
Validation: cargo nextest run -p foo abc_020
Expected output: code changes, passing validation, TODO.md status update, evidence note
```

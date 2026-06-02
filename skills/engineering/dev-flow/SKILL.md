---
name: dev-flow
description: >
  Routes large Rust project work through the user's Codex workflow: audit repo scale, bootstrap
  docs, grill requirements, shape product architecture, open or reuse workstreams, run architecture
  lanes, orchestrate multi-agent execution, debug, test, review, and close out. Use when starting
  development, planning a feature/refactor, assigning a lane, or asking "which skill should we use now?"
---

# Dev Flow

Use this as the orchestrator skill for large Rust development. The user should be able to start with
only `$dev-flow`; route to specialized skills and carry their output into the next phase.

## First Move

Classify the request before coding:

- Repo scale, old docs, or architecture-lane fit is unclear -> `audit-project-scale`.
- Medium/large repo lacks workflow docs -> `setup-rust-workstreams`.
- Requirement is fuzzy or risky -> `grill-with-docs`.
- Broad product ambition, MVP ladder, or capability map is unclear -> `shape-product-architecture`.
- Durable feature/refactor, cross-crate work, or multi-agent work -> `open-workstream`.
- Upper planning for large multi-lane work -> `plan-engineering-program`.
- Long-lived terminal for one architecture area -> `run-architecture-lane`.
- Completed lane/worker/worktree result needs intake -> `integrate-lane-results`.
- Existing workstream continuation -> `resume-workstream`.
- One bounded task from `TODO.md` -> `run-workstream-task`.
- Completed task or worker handoff needs review -> `review-workstream`.
- Completion claim needs fresh evidence -> `verify-rust-workstream`.
- Small one-off testable change outside a workstream -> `tdd`; do not bootstrap docs.
- Bug, failure, flake, or perf regression outside a workstream -> `diagnose`.
- Selected architecture direction -> `plan-architecture-lane`; architecture cleanup -> `improve-codebase-architecture`; confirmed refactor -> `fearless-refactor`.
- Unfamiliar code blocks planning -> `zoom-out`, then return here.
- Lane appears complete -> `close-workstream`.
- Session transfer -> `handoff`.
- External tracker artifacts -> `to-prd` then `to-issues` only when useful.

Read runtime, artifact, agent-contract, gate, worktree-safety, side-effect-policy, context-budget,
router, documentation-authority, and source-coverage references when classification or state is unclear.

## Delegation Rules

Actively delegate instead of only suggesting a skill:

- Use `grill-with-docs` before durable planning when terms, risks, or boundaries are unclear.
- Use `shape-product-architecture` before workstreams when product/MVP/capability direction is unclear.
- Use `audit-project-scale` before setup or lane planning when repo scale or old docs are unclear.
- Use `plan-architecture-lane` before workstream creation for a selected architecture direction.
- Use `open-workstream` only for durable lanes, not tiny tasks.
- Use `plan-engineering-program` for the upper architecture / commander terminal in large projects.
- Use `run-architecture-lane` only for large projects with capability-scoped terminal ownership.
- Use `integrate-lane-results` for worker/lane result intake, review/verify routing, and sync.
- Use `run-workstream-task` for task-ledger slices; it routes to `tdd` or `diagnose`.
- Use `review-workstream` before accepting worker output or closeout readiness.
- Use `verify-rust-workstream` before marking tasks, goals, or lanes complete.
- After `audit-project-scale`, if the repo has no active workstream substrate, no lane pressure, no
  shared-scope arbitration need, and the prompt is a bounded engineering task, downshift
  immediately to `tdd`, `diagnose`, or one lightweight workstream path. Do not stop at
  planner-only read-only inspection when the user actually needs implementation routing.
- Use Codex goals only for one bounded task, approved lane bundle, or docs-backed lane campaign.
- When a delegated skill finishes, return here and choose the next phase.
- Do not make the user manually remember the chain.

## Development Flow

1. Audit repo scale when workflow shape or old docs are unclear.
2. Bootstrap missing `AGENTS.md`, `CONTEXT.md`, and `docs/workstreams/`.
3. Clarify risky work before planning.
4. Shape product architecture and MVP ladders when the ambition spans stages or client surfaces.
5. Choose planning depth and the smallest workflow scale: direct task, workstream, or architecture lane.
6. Open or reuse a workstream for durable multi-slice work.
7. Split work by independently validatable vertical slices.
8. Execute one bounded task at a time; review and verify with fresh targeted gates.
9. Record durable decisions in ADRs or workstream docs, then close satisfied lanes or split follow-ons.

## Output Contract

For each phase transition, say the current phase, delegated skill, expected artifact, artifact path,
user action or approval needed, and next likely phase.

For large-repo orchestration or planner-style routing, also report:

- `Operating Mode: READINESS | AUDIT`
- `Implementation Horizon: <N>`
- whether blockers affect the active queue or only historical audit quality

Use `READINESS` when you are deciding what can safely run next from the active queue.
Use `AUDIT` when you are inspecting historical quality, evidence drift, or closeout hygiene without
yet assigning implementation.

Example:

```text
Phase: planning
Delegating to: open-workstream
Expected artifact: docs/workstreams/<slug>/TODO.md task ledger
Next phase: execute the first bounded task with run-workstream-task
```

Large-repo planner-style example:

```text
Phase: planning
Operating Mode: READINESS
Implementation Horizon: 1
Delegating to: plan-engineering-program
Expected artifact: ready active queue summary plus next bounded assignment recommendation
Next phase: assign the first bounded task or lane bundle
```

## Multi-Agent Defaults

- Upper planner owns sequencing; lane terminals own capability areas; workers own bounded slices.
- Reviewers check workstream contract and repo standards before fresh verification.
- Parallel workers need disjoint scopes, and every terminal returns the marker in `agent-contracts.md`.

Read `references/multi-agent-flow.md`, `references/agent-contracts.md`, and `references/worktree-safety.md` before launching multiple workers.

## Artifact Rule

Authority order: product docs -> ADRs -> workstream docs -> task ledger -> journals/handoff -> chat. Never let journals become the only place where important decisions live.
Use `references/artifact-contracts.md` to distinguish control state from recovery narrative.

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

Classify before coding and delegate immediately. Read `references/skill-router.md` before selecting
a route; the quick list below is only a memory aid:

- unclear scale, stale docs, or lane fit -> `audit-project-scale`
- unclear requirements -> `grill-with-docs`; broad product ambition -> `shape-product-architecture`
- durable multi-slice work -> `open-workstream`; one task from a ledger -> `run-workstream-task`
- upper multi-lane planning -> `plan-engineering-program`; long-lived lane terminal -> `run-architecture-lane`
- lane/worker result intake -> `integrate-lane-results`; review -> `review-workstream`; proof -> `verify-rust-workstream`
- small direct change -> `tdd`; bug/perf failure -> `diagnose`; unfamiliar code -> `zoom-out`

Read runtime, artifact, agent-contract, gate, worktree-safety, side-effect-policy, context-budget,
documentation-authority, and source-coverage references only when classification or state is unclear.

## Delegation Rules

Actively delegate instead of only suggesting a skill. After a delegated skill finishes, return here
and choose the next phase.

- Use the smallest workflow scale that protects the work; do not bootstrap docs for tiny direct tasks.
- After `audit-project-scale`, downshift to `tdd`, `diagnose`, or one lightweight workstream path
  when there is no active workstream substrate, no lane pressure, and the prompt is bounded.
- Use Codex goals only for one bounded task, approved lane bundle, or docs-backed lane campaign.
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

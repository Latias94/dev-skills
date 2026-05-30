---
name: dev-flow
description: >
  Routes large Rust project work through the user's Codex workflow: audit repo scale, bootstrap
  docs, grill requirements, open or reuse workstreams, run architecture lanes, coordinate
  multi-agent execution, debug, test, review, and close out. Use when starting development,
  planning a feature/refactor, assigning an architecture lane, or asking "which skill should we use now?"
---

# Dev Flow

Use this as the orchestrator skill for large Rust development. The user should be able to start with
only `$dev-flow`; route to specialized skills and carry their output into the next phase.

## First Move

Classify the request before coding:

- Repo scale, old docs, or architecture-lane fit is unclear -> `audit-project-scale`.
- Medium/large repo lacks workflow docs -> `setup-rust-workstreams`.
- Requirement is fuzzy or risky -> `grill-with-docs`.
- Durable feature/refactor, cross-crate work, or multi-agent work -> `open-workstream`.
- Long-lived terminal for one architecture area -> `run-architecture-lane`.
- Multiple active terminals on one workstream -> `coordinate-workstream`.
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

Read `references/skill-router.md`, `references/stage-map.md`, and `references/documentation-authority.md` when classification, user next action, or documentation updates are not obvious.

## Delegation Rules

Actively delegate instead of only suggesting a skill:

- Use `grill-with-docs` before durable planning when terms, risks, or boundaries are unclear.
- Use `audit-project-scale` before setup or lane planning when repo scale or old docs are unclear.
- Use `plan-architecture-lane` before workstream creation when the user picked an architecture
  direction; it delegates to `improve-codebase-architecture` when lane seams or docs/code alignment are unclear.
- Use `open-workstream` only for durable lanes, not tiny tasks.
- Use `run-architecture-lane` only for large projects with capability-scoped terminal ownership.
- Use `coordinate-workstream` for planner / PM terminal coordination.
- Use `run-workstream-task` for task-ledger slices; it routes to `tdd` or `diagnose`.
- Use `review-workstream` before accepting worker output or closeout readiness.
- Use `verify-rust-workstream` before marking tasks, goals, or lanes complete.
- Use Codex goals only for one bounded task from `TODO.md` or one planner-approved lane goal
  bundle. Do not bind a goal to an entire architecture lane.
- When a delegated skill finishes, return here and choose the next phase.
- Do not make the user manually remember the chain.

## Development Flow

1. Audit repo scale when workflow shape or old docs are unclear.
2. Bootstrap missing `AGENTS.md`, `CONTEXT.md`, and `docs/workstreams/`.
3. Clarify risky work before planning.
4. Choose planning depth and the smallest workflow scale: direct task, workstream, or architecture lane.
5. Open or reuse a workstream for durable multi-slice work.
6. Split work by independently validatable vertical slices.
7. Execute one bounded task at a time.
8. Review completed slices against workstream contract and code quality.
9. Verify with fresh targeted gates, then broader gates before closeout.
10. Record durable decisions in ADRs or workstream docs.
11. Close satisfied lanes or split follow-ons.

## Output Contract

For each phase transition, say the current phase, delegated skill, expected artifact, artifact path,
user action or approval needed, and next likely phase.

Example:

```text
Phase: planning
Delegating to: open-workstream
Expected artifact: docs/workstreams/<slug>/TODO.md task ledger
Next phase: execute the first bounded task with run-workstream-task
```

## Multi-Agent Defaults

- One planner owns workstream creation/reuse, decomposition, lane bundles, and conflict resolution.
- Architecture-lane terminals own capability areas, not global scope.
- Workers own bounded slices and should not rewrite the whole plan.
- Reviewers use `review-workstream` to check repo standards and workstream contract.
- Parallel workers should have disjoint file scopes or explicitly serialized tasks.

Read `references/multi-agent-flow.md` before launching multiple workers.

## Artifact Rule

Authority order: ADRs -> workstream docs -> task ledger -> journals/handoff -> chat. Never let
journals become the only place where important decisions live.

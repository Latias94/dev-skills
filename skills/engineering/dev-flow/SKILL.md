---
name: dev-flow
description: >
  Routes large Rust project work through the user's Codex workflow: choose the right skill, decide
  whether to bootstrap docs, grill requirements, open or reuse a workstream, split tasks, run
  multi-agent execution, debug, test, review, and close out. Use when starting a new development
  session, planning a feature/refactor, coordinating multiple agents, or asking "which skill should
  we use now?"
---

# Dev Flow

Use this as the orchestrator skill for large Rust development.

The user should be able to start with only `$dev-flow`. Route the work to the right specialized
skill, then carry that output into the next phase.

## First Move

Classify the request before coding:

- Repo lacks workflow docs -> `setup-rust-workstreams`.
- Requirement is fuzzy or risky -> `grill-with-docs`.
- Durable feature/refactor, cross-crate work, or multi-agent work -> `open-workstream`.
- Multiple active terminals on one workstream -> `coordinate-workstream`.
- Existing workstream continuation -> `resume-workstream`.
- One bounded task from `TODO.md` -> `run-workstream-task`.
- Completed task or worker handoff needs review -> `review-workstream`.
- Completion claim needs fresh evidence -> `verify-rust-workstream`.
- Small testable change outside a workstream -> `tdd`.
- Bug, failure, flake, or perf regression outside a workstream -> `diagnose`.
- Architecture cleanup -> `improve-codebase-architecture`.
- Unfamiliar code blocks planning -> `zoom-out`, then return here.
- Lane appears complete -> `close-workstream`.
- Session transfer -> `handoff`.
- External tracker artifacts -> `to-prd` then `to-issues` only when useful.

Read `references/skill-router.md` when classification is not obvious.

## Delegation Rules

Actively delegate instead of only suggesting a skill:

- Use `grill-with-docs` before durable planning when terms, risks, or boundaries are unclear.
- Use `open-workstream` only for durable lanes, not tiny tasks.
- Use `coordinate-workstream` for planner / PM terminal coordination.
- Use `run-workstream-task` for task-ledger slices; it routes to `tdd` or `diagnose`.
- Use `review-workstream` before accepting worker output or closeout readiness.
- Use `verify-rust-workstream` before marking tasks, goals, or lanes complete.
- Use Codex goals only for one bounded task from `TODO.md`.
- When a delegated skill finishes, return here and choose the next phase.
- Do not make the user manually remember the chain.

## Development Flow

1. Bootstrap missing `AGENTS.md`, `CONTEXT.md`, and `docs/workstreams/`.
2. Clarify risky work before planning.
3. Open or reuse a workstream for durable multi-slice work.
4. Split work by independently validatable vertical slices.
5. Execute one bounded task at a time.
6. Review completed slices against workstream contract and code quality.
7. Verify with fresh targeted gates, then broader gates before closeout.
8. Record durable decisions in ADRs or workstream docs.
9. Close satisfied lanes or split follow-ons.

## Output Contract

For each phase transition, say:

- current phase,
- delegated skill,
- expected artifact,
- where the artifact will live,
- and the next likely phase.

Example:

```text
Phase: planning
Delegating to: open-workstream
Expected artifact: docs/workstreams/<slug>/TODO.md task ledger
Next phase: execute the first bounded task with run-workstream-task
```

## Multi-Agent Defaults

- One planner owns decomposition and conflict resolution.
- Workers own bounded slices and should not rewrite the whole plan.
- Reviewers use `review-workstream` to check repo standards and workstream contract.
- Parallel workers should have disjoint file scopes or explicitly serialized tasks.

Read `references/multi-agent-flow.md` before launching multiple workers.

## Artifact Rule

Authority order: ADRs -> workstream docs -> task ledger -> journals/handoff -> chat.

Never let journals become the only place where important decisions live.

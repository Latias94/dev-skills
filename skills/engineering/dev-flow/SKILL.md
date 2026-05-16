---
name: dev-flow
description: >
  Route large Rust project work through the user's Codex workflow: choose the right skill, decide
  whether to bootstrap docs, grill requirements, open or reuse a workstream, split tasks, run
  multi-agent execution, debug, test, review, and close out. Use when starting a new development
  session, planning a feature/refactor, coordinating multiple agents, or asking "which skill should
  we use now?"
---

# Dev Flow

Use this as the orchestrator skill for large Rust development.

The user should be able to start with only `$dev-flow`. After that, route the work to the right
specialized skill and carry its output into the next phase.

## First Move

Classify the request before coding:

- **Repo not initialized for this workflow** -> use `setup-rust-workstreams`.
- **Requirement is fuzzy or risky** -> use `grill-with-docs`.
- **Large feature/refactor** -> use `open-workstream`.
- **Existing workstream continuation** -> use `resume-workstream`.
- **One bounded workstream task** -> use `run-workstream-task`.
- **Small bounded code change outside a workstream** -> use `tdd` if behavior is testable.
- **Bug, failure, or performance regression outside a workstream** -> use `diagnose`.
- **Architecture cleanup request** -> use `improve-codebase-architecture`.
- **Lane appears complete** -> use `close-workstream`.
- **Need session transfer** -> use `handoff`.
- **Need external issue tracking** -> use `to-prd` then `to-issues` only when useful.

Read `references/skill-router.md` when classification is not obvious.

## Delegation Rules

Actively delegate instead of only suggesting a skill:

- If the repo lacks workflow docs, stop feature work and invoke `setup-rust-workstreams`.
- If requirements, terms, risks, or architecture boundaries are unclear, invoke `grill-with-docs`
  before creating a workstream.
- If the work is durable, multi-slice, cross-crate, or multi-agent, invoke `open-workstream`.
- If resuming an existing lane, invoke `resume-workstream`.
- If a task from `TODO.md` is ready, invoke `run-workstream-task`; it will route to `tdd` or
  `diagnose`.
- If a small task is outside a workstream and behavior-testable, invoke `tdd`.
- If a failure is outside a workstream, invoke `diagnose`.
- If a lane target appears complete, invoke `close-workstream`.
- If unfamiliar code blocks planning, invoke `zoom-out`, then return to the router.
- If the user wants external tracker artifacts, invoke `to-prd` and then `to-issues` only when
  issue export is useful.
- If the session is ending or another agent will continue, invoke `handoff`.

When a delegated skill finishes, resume this router and choose the next phase. Do not make the user
manually remember the whole chain.

## Development Flow

1. **Bootstrap**
   - Check for `AGENTS.md`, `CONTEXT.md`, and `docs/workstreams/`.
   - If missing, invoke `setup-rust-workstreams`.
2. **Clarify**
   - Use `grill-with-docs` for unclear goals, new product behavior, architecture-sensitive
     changes, or terminology drift.
3. **Plan**
   - Use `open-workstream` for durable lanes.
   - Reuse an existing workstream when the goal fits.
   - Create a new workstream only for a durable goal with multiple slices and gates.
4. **Split**
   - Planner writes the task ledger.
   - Split by independently validatable vertical slices.
   - Keep tasks in `docs/workstreams/<slug>/TODO.md`.
5. **Execute**
   - Single worker: use `run-workstream-task` for task-ledger slices.
   - Multiple workers: assign disjoint tasks from the ledger.
6. **Record**
   - Durable decisions go to ADRs or workstream docs.
   - Session details go to `JOURNAL/` or `HANDOFF.md`.
7. **Verify**
   - Run targeted gates during iteration.
   - Run broader gates before closeout when feasible.
8. **Close**
   - Invoke `close-workstream` to update `EVIDENCE_AND_GATES.md`, `MILESTONES.md`,
     `WORKSTREAM.json`, and closeout notes.
   - Split follow-ons instead of widening a lane indefinitely.

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
- Workers own bounded task slices and should not rewrite the whole plan.
- Reviewers check both repo standards and workstream contract.
- Parallel workers should have disjoint file scopes or explicitly serialized tasks.

Read `references/multi-agent-flow.md` before launching multiple workers.

## Artifact Rule

The workflow is Trellis-like in experience, but not Trellis-like in authority:

1. ADRs define long-term contracts.
2. Workstreams define durable execution lanes.
3. Task ledgers coordinate multi-agent work.
4. Journals and handoffs help resume sessions.

Never let journals become the only place where important decisions live.

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

Use this as the entrypoint skill for large Rust development.

## First Move

Classify the request before coding:

- **Repo not initialized for this workflow** -> use `bootstrap-rust-project`.
- **Requirement is fuzzy or risky** -> use `grill-with-docs`.
- **Large feature/refactor** -> use `rust-workstream`.
- **Small bounded code change** -> use `tdd` if behavior is testable.
- **Bug, failure, or performance regression** -> use `diagnose`.
- **Architecture cleanup request** -> use `improve-codebase-architecture`.
- **Need session transfer** -> use `handoff`.
- **Need external issue tracking** -> use `to-prd` then `to-issues` only when useful.

Read `references/skill-router.md` when classification is not obvious.

## Development Flow

1. **Bootstrap**
   - Check for `AGENTS.md`, `CONTEXT.md`, and `docs/workstreams/`.
   - If missing, invoke `bootstrap-rust-project`.
2. **Clarify**
   - Use `grill-with-docs` for unclear goals, new product behavior, architecture-sensitive
     changes, or terminology drift.
3. **Plan**
   - Use `rust-workstream` for durable lanes.
   - Reuse an existing workstream when the goal fits.
   - Create a new workstream only for a durable goal with multiple slices and gates.
4. **Split**
   - Planner writes the task ledger.
   - Split by independently validatable vertical slices.
   - Keep tasks in `docs/workstreams/<slug>/TODO.md`.
5. **Execute**
   - Single worker: use `tdd` for feature slices or `diagnose` for bugs.
   - Multiple workers: assign disjoint tasks from the ledger.
6. **Record**
   - Durable decisions go to ADRs or workstream docs.
   - Session details go to `JOURNAL/` or `HANDOFF.md`.
7. **Verify**
   - Run targeted gates during iteration.
   - Run broader gates before closeout when feasible.
8. **Close**
   - Update `EVIDENCE_AND_GATES.md`, `MILESTONES.md`, `WORKSTREAM.json`, and closeout notes.
   - Split follow-ons instead of widening a lane indefinitely.

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

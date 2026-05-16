---
name: rust-workstream
description: >
  Run large Rust project development through an ADR/workstream/task-ledger workflow. Use when the
  user wants Trellis-like execution experience without replacing existing ADRs, when planning or
  executing a large Rust feature/refactor, when coordinating multiple agents, or when deciding how
  to split work into workstreams, tasks, journals, and handoffs.
---

# Rust Workstream

Use this skill to coordinate large Rust work without creating duplicate sources of truth.

## Compose With Upstream Skills

This workflow assumes these skills may be installed separately:

- `grill-with-docs`: clarify requirements and challenge terminology before planning.
- `to-prd`: turn an already-clarified conversation into product/spec input.
- `to-issues`: export task slices to an issue tracker when needed.
- `tdd`: execute feature slices with red-green-refactor.
- `diagnose`: debug hard failures and performance regressions.
- `handoff`: compact a session for another agent.
- `improve-codebase-architecture`: periodically find refactor/deepening opportunities.

Read `references/upstream-skills.md` when deciding which upstream skill should own a phase.

## Source Of Truth Order

1. Accepted ADRs and architecture contracts
2. Workstream `DESIGN.md`, `MILESTONES.md`, `EVIDENCE_AND_GATES.md`
3. Workstream `TODO.md` task ledger
4. `HANDOFF.md` and `JOURNAL/`
5. Chat history

If a lower layer conflicts with a higher layer, stop and surface the conflict.

## Choose The Artifact

- Create a new workstream for a durable goal with multiple slices and validation gates.
- Add tasks to an existing workstream when the goal and contract boundary already exist.
- Add a follow-on workstream when scope is independently closeable or changes the contract.
- Use a journal entry only for session history and resume context.
- Use issues only when external tracking or parallel assignment needs them.

Read `references/task-decomposition.md` before splitting work.
Read `references/multi-agent.md` before assigning workers.

## Workflow

1. **Clarify**
   - If requirements are fuzzy, run the `grill-with-docs` style interview first.
   - Identify relevant ADRs, docs, crates, tests, and existing workstreams.
2. **Open or select a workstream**
   - Reuse an active workstream if the goal fits.
   - Open a new workstream only when there is a durable lane.
   - Start from `assets/workstream-template/` when creating one.
3. **Freeze scope**
   - Write problem, target state, in-scope, out-of-scope, assumptions, and gates.
   - If a hard-to-change contract is being created or changed, propose an ADR.
4. **Split tasks**
   - Use vertical slices with owner, dependencies, file scope, validation, and handoff notes.
   - Keep the task ledger in `TODO.md`.
   - Do not create a workstream per task.
5. **Coordinate execution**
   - Assign one worker per bounded task or disjoint file scope.
   - Workers update only their task status, journal entry, and evidence notes.
   - Planner resolves dependency or scope conflicts.
6. **Verify and close**
   - Run targeted gates during iteration and broader gates before closeout.
   - Move evidence into `EVIDENCE_AND_GATES.md`.
   - Close the lane with a status note or split a follow-on.

## Task Ledger Format

Use this compact task shape in `TODO.md`:

```md
- [ ] WS-120 [owner=agent-a] [deps=WS-110] [scope=crates/foo,tests/foo]
  Goal: Add the narrow behavior that makes the slice independently useful.
  Validation: cargo nextest run -p foo targeted_test_name
  Evidence: path/to/test.rs, docs/workstreams/<slug>/EVIDENCE_AND_GATES.md
  Handoff: Notes another worker needs.
```

## Safety Rules

- Never let workers independently rewrite the whole task ledger.
- Never let session journals override ADRs or workstream design.
- Never split by "backend/frontend/tests" if a vertical slice can be formed.
- Do not commit without user confirmation.
- For large Rust workspaces, prefer targeted `cargo nextest run` during iteration.

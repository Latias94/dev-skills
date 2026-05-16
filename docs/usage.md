# Usage

Most users should start with `$dev-flow`.

`$dev-flow` is the orchestrator. It should actively delegate to the next skill instead of only
telling the user what to do next.

## Common Calls

Initialize a project:

```text
Use $dev-flow to initialize this Rust repo for the dev-skills workflow.
```

Direct setup:

```text
Use $setup-rust-workstreams to add AGENTS.md, CONTEXT.md, and docs/workstreams conventions to this Rust repo.
```

Plan a large feature:

```text
Use $dev-flow to plan this feature. If it is large enough, open a workstream and split tasks.
```

Start a workstream directly:

```text
Use $open-workstream to create a workstream for this refactor and write the task ledger.
```

Resume a workstream:

```text
Use $resume-workstream to reconstruct the current state and recommend the next task.
```

Close a workstream:

```text
Use $close-workstream to finalize evidence, gates, status, and follow-ons for this lane.
```

Clarify requirements before planning:

```text
Use $grill-with-docs to pressure-test this plan against the repo docs and ADRs.
```

Implement a bounded task:

```text
Use $run-workstream-task to execute task ABC-020 from docs/workstreams/<slug>/TODO.md.
```

Debug a failure:

```text
Use $diagnose to reproduce and fix this failing test.
```

Prepare a handoff:

```text
Use $handoff to summarize this session and update the workstream handoff notes.
```

## Default User Experience

```text
User -> $dev-flow -> delegated skill -> $dev-flow resumes routing
```

The user should not need to remember every skill. `$dev-flow` should decide whether the next move is
bootstrap, grill, workstream planning, TDD execution, diagnosis, review, or handoff.

Example chain:

```text
User asks for large feature
-> $dev-flow detects unclear requirements
-> delegates to $grill-with-docs
-> resumes and delegates to $open-workstream
-> creates task ledger
-> delegates first task to $tdd or $diagnose
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
4. Agent marks the goal complete only after the task is genuinely done.
5. Agent updates TODO.md and EVIDENCE_AND_GATES.md.
```

## Multi-Agent Use

Only parallelize when tasks have clear boundaries.

Planner prompt:

```text
Use $open-workstream to split this workstream into parallel-safe worker tasks with owners, scopes,
dependencies, and validation commands.
```

Worker prompt:

```text
Use $run-workstream-task to execute task ABC-020. It should delegate to $tdd or $diagnose as needed,
stay within the assigned file scope, and update the task ledger and journal when done.
```

Reviewer prompt:

```text
Review the completed tasks against the workstream contract and repo standards.
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

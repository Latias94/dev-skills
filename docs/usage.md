# Usage

Chinese documentation: [zh-CN/usage.md](./zh-CN/usage.md)

Most users should start with `$dev-flow`.

`$dev-flow` is the orchestrator. It should actively delegate to the next skill instead of only
telling the user what to do next.

## Common User Calls

Initialize a project:

```text
Use $dev-flow to initialize this Rust repo for the dev-skills workflow.
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

Coordinate multiple terminals:

```text
Use $coordinate-workstream to coordinate the active workstream across planner, worker, reviewer,
and docs terminals.
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

## Default User Experience

```text
User -> $dev-flow -> delegated skill -> $dev-flow resumes routing
```

The user should not need to remember internal workflow skills. `$dev-flow` should decide whether the
next move is bootstrap, grill, workstream planning, TDD execution, diagnosis, review, or handoff.

Example chain:

```text
User asks for large feature
-> $dev-flow detects unclear requirements
-> delegates to $grill-with-docs
-> resumes and delegates to $open-workstream
-> creates task ledger
-> delegates multi-terminal planning to $coordinate-workstream when needed
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

## Internal Workflow Skills

These are normally invoked by `$dev-flow`, not manually:

- `setup-rust-workstreams`
- `open-workstream`
- `coordinate-workstream`
- `resume-workstream`
- `run-workstream-task`
- `close-workstream`

Directly call one only when you intentionally want to bypass the router, or when the planner terminal
is actively coordinating multiple terminals with `coordinate-workstream`.

## Multi-Agent Use

Only parallelize when tasks have clear boundaries.

Planner prompt:

```text
Use $coordinate-workstream to prepare parallel work for the active workstream.
Assign tasks only when owners, scopes, dependencies, and validation commands are clear.
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

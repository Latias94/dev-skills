# Repository Guidelines

## Project Context

Describe what this Rust project is, who it serves, and which architectural constraints matter.

## Architecture Boundaries

- Document crate ownership and dependency direction.
- Keep contract crates free of platform-specific dependencies unless explicitly accepted.
- Prefer ADR evidence over local intuition for hard-to-change behavior.

## Build, Test, And Development Commands

- `cargo build --workspace`
- `cargo fmt`
- `cargo nextest run` when available
- `cargo test --workspace` when nextest is unavailable
- `cargo clippy --workspace --all-targets -- -D warnings`

For large workspaces, prefer targeted package/test commands during iteration and run broader gates
before closeout.

## Documentation And Workstreams

- ADRs in `docs/adr/` are the highest source of truth for accepted architecture contracts.
- Workstreams in `docs/workstreams/<slug>/` own durable design and execution lanes.
- A workstream task ledger is the canonical multi-agent task list.
- Session journals and handoffs are resume aids, not architecture truth.

## Default Skill Routing

For non-trivial Rust development, apply `$dev-flow` routing even when the user does not explicitly
name it:

- missing workflow docs -> `$setup-rust-workstreams`
- unclear or risky requirements -> `$grill-with-docs`
- durable multi-slice work -> `$open-workstream`
- multiple active terminals on one lane -> `$coordinate-workstream`
- resume an existing lane -> `$resume-workstream`
- bounded feature slice -> `$run-workstream-task` then `$tdd`
- bug, regression, or performance issue -> `$run-workstream-task` then `$diagnose`
- session transfer -> `$handoff`
- lane closeout -> `$close-workstream`

Use Codex goals for one bounded task from the task ledger, not for the whole workstream.

## Multi-Agent Rules

- One planner owns task decomposition.
- Workers own bounded vertical slices from the task ledger.
- Workers must not rewrite global scope without escalation.
- Each worker records touched files, validation, and follow-up notes.

## Git Safety

- Do not revert user changes without explicit approval.
- Do not use destructive git commands unless explicitly requested.
- Stage only files relevant to the current task.
- Ask before committing.

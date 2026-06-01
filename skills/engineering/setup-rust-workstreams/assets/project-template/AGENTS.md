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
- Architecture maps in `docs/architecture/` route large capability areas and lane ownership.
- Long-term lane maturity and backlog live in architecture docs; Codex goals cover only current
  bounded tasks, lane bundles, or approved lane campaigns.
- Workstreams in `docs/workstreams/<slug>/` own durable design and execution lanes.
- `TODO.md` is the human task ledger; `TASKS.jsonl` is the machine-readable task state.
- `CAMPAIGNS.jsonl` records approved medium autonomous campaign order, gates, and stop conditions.
- `CONTEXT.jsonl` manifests point workers at required ADRs, architecture docs, evidence, and research.
- Session journals and handoffs are resume aids, not architecture truth.

## Default Skill Routing

For non-trivial Rust development, apply `$dev-flow` routing even when the user does not explicitly
name it:

- missing workflow docs -> `$setup-rust-workstreams`
- unclear repo scale, old docs, or lane fit -> `$audit-project-scale`
- small one-off change -> `$tdd` or `$diagnose`
- unclear or risky requirements -> `$grill-with-docs`
- durable multi-slice work -> `$open-workstream`
- selected architecture direction before workstream creation -> `$plan-architecture-lane`
- long-lived terminal for one architecture area -> `$run-architecture-lane`
- multiple lanes or terminals need macro sequencing -> `$plan-engineering-program`
- completed lane/worktree output needs intake -> `$integrate-lane-results`
- resume an existing lane -> `$resume-workstream`
- bounded feature slice -> `$run-workstream-task` then `$tdd`
- bug, regression, or performance issue -> `$run-workstream-task` then `$diagnose`
- session transfer -> `$handoff`
- lane closeout -> `$close-workstream`

Use Codex goals for one bounded task from the task ledger, one approved lane goal bundle, or
one approved lane campaign, not for the whole workstream or an entire architecture lane.

## Multi-Agent Rules

- One upper architecture planner owns lane maps, campaigns, and global sequence.
- Upper planner keeps machine-readable task/campaign state aligned with the human ledger.
- Upper planner uses `$plan-engineering-program` and `$plan-architecture-lane` to choose planning depth
  before assigning bundles.
- Upper planner writes Codex goals to set for approved tasks, lane bundles, or lane campaigns, never for an
  entire architecture lane.
- Workers own bounded vertical slices from the task ledger.
- Architecture lane terminals own capability areas, not global scope, and run only within the
  approved lane bundle or campaign.
- Workers may propose follow-ups or splits, but must not rewrite global scope or target state.
- Each worker reads assigned context before editing and records touched files, validation, and
  follow-up notes.
- Upper planner/integrator terminals may keep local runtime state in `.codex/planner-state.local.json`; do not treat
  absolute paths as architecture truth.

## Git Safety

- Do not revert user changes without explicit approval.
- Do not use destructive git commands unless explicitly requested.
- Stage only files relevant to the current task.
- Ask before committing unless the active campaign policy explicitly pre-approves task-boundary
  commits after review, fresh gates, and clean scope checks.

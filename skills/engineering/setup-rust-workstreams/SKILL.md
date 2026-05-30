---
name: setup-rust-workstreams
description: >
  Sets up Codex-friendly ADR/workstream workflow docs for a Rust repo. Use when initializing a new
  Rust project, migrating an existing repo to the dev-skills workflow, or adding AGENTS.md,
  CONTEXT.md, docs/workstreams/, optional docs/architecture lane maps, task-ledger rules, Rust
  validation commands, and multi-agent guardrails.
---

# Setup Rust Workstreams

Initialize the project substrate. Do not plan a feature in this skill. If repo scale or lane fit is
unclear, route through `audit-project-scale` first.

## Inspect First

Read only what is needed:

- `Cargo.toml` and workspace shape
- existing `AGENTS.md`, `CLAUDE.md`, `CONTEXT.md`
- `docs/`, `docs/adr/`, `docs/architecture/`, `docs/workstreams/`
- `.config/nextest.toml` and CI workflows
- current git status

Preserve existing project rules. Add missing sections rather than replacing local policy.

## Write

For medium or large Rust repos, create or update:

- `AGENTS.md`
- `CONTEXT.md`
- `docs/architecture/README.md` and `LANES.md` for large multi-lane repos
- `docs/workstreams/README.md`

Use `assets/project-template/` only when the repo has no equivalent files.
Read `references/project-layout.md` before adapting templates.

## Required Rules

- ADRs outrank workstreams when `docs/adr/` exists.
- Workstreams own durable lanes, not tiny tasks.
- Architecture maps route large capability areas; workstreams own execution evidence.
- `TODO.md` is the task ledger for multi-agent work.
- `JOURNAL/` and `HANDOFF.md` are session memory, not architecture truth.
- Prefer `cargo nextest run` when available.
- Review completed work before accepting it into the lane.
- Record fresh verification evidence before completion claims.
- Use Codex goals only for one bounded task from the task ledger.

## Example

```text
Use $setup-rust-workstreams to initialize this Rust repo for ADR/workstream-based Codex development.
```

## Output

Report:

- files created or updated,
- project conventions preserved,
- whether the repo is ready for `$dev-flow`,
- whether architecture lanes are useful or overkill,
- and any setup gaps.

Do not commit without user confirmation.

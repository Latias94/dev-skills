---
name: bootstrap-rust-project
description: >
  Initialize Codex-friendly workflow docs for a large Rust project: AGENTS.md, CONTEXT.md,
  docs/workstreams/, ADR conventions, testing commands, task ledger rules, and multi-agent safety
  guardrails. Use when setting up a new Rust repo, migrating an existing Rust repo to the user's
  workstream process, or applying dev-skills workflow conventions across projects.
---

# Bootstrap Rust Project

Set up a large Rust project so Codex can work safely across sessions and agents.

## Inputs

Inspect the repo before writing:

- `Cargo.toml` and workspace layout
- existing `AGENTS.md`, `CLAUDE.md`, `CONTEXT.md`
- `docs/`, `docs/adr/`, `docs/workstreams/`
- `.config/nextest.toml`, CI workflows, test commands
- current git status

If project-specific rules already exist, preserve them and add only missing workflow sections.

## Process

1. Identify whether the repo is small, medium, or large:
   - Small: one crate, few docs, no long-lived architecture lanes.
   - Medium: workspace or multiple apps/crates, some tests and docs.
   - Large: workspace, ADRs, cross-crate contracts, long-running refactors, or multi-agent work.
2. For medium/large projects, create or update:
   - `AGENTS.md`
   - `CONTEXT.md`
   - `docs/workstreams/README.md`
3. If `docs/adr/` exists, document that ADRs outrank workstreams.
4. If `docs/adr/` does not exist, do not create ADRs automatically unless the user asks; note the
   intended relationship in `docs/workstreams/README.md`.
5. Add Rust command guidance:
   - Prefer `cargo nextest run` when available.
   - Use `cargo fmt` for formatting.
   - Use targeted test commands for large workspaces when full runs are too slow.
6. Add multi-agent rules:
   - One planner owns task decomposition.
   - Workers own bounded slices.
   - Workers do not rewrite global scope without escalation.
   - Session journals are handoff aids, not architecture truth.

## Templates

Use `assets/project-template/` as a starting point when a repo has no equivalent files.

Read `references/project-layout.md` before adapting the templates.

## Output

Report:

- files created or updated
- existing project conventions preserved
- recommended first workstream, if obvious
- any unresolved setup questions

Do not commit without user confirmation.

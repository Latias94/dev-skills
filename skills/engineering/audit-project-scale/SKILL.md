---
name: audit-project-scale
description: >
  Audits a Rust repo's size, workflow docs, architecture docs, workstreams, and multi-terminal
  readiness before choosing a dev-skills path. Use when starting or migrating a repo, when old
  workstream or architecture docs may need repair, when deciding between direct tasks,
  workstreams, architecture lanes, planner terminals, or multi-agent development, or when the user
  asks which dev-skills workflow fits this repository.
---

# Audit Project Scale

Use this before durable planning when the right workflow scale is unclear.

This skill classifies the repo and routes to the next skill. It should not implement product work,
rewrite architecture decisions, or create a workstream by itself.

## Inspect

Read only what is needed:

- `Cargo.toml`, workspace members, crate boundaries, binaries, examples, and tests
- `AGENTS.md`, `CONTEXT.md`, `CLAUDE.md`, and repo-specific development rules
- `docs/adr/`, `docs/architecture/`, `docs/workstreams/`, and active `WORKSTREAM.json`
- `.config/nextest.toml`, CI workflows, and common validation commands
- git status, current branch, linked worktrees, and obvious dirty scopes

If the user gives Codex session IDs or says state was lost, use `codex-session-recovery` only as
supporting evidence. Project docs and git state still outrank recovered chat.

## Classify

- **Small repo**: one crate or simple workspace, one terminal, short-lived changes. Prefer
  `$dev-flow`, which may route straight to `tdd` or `diagnose`. Do not add architecture lanes.
- **Medium repo**: multi-step feature/refactor, cross-module or cross-crate work, but not enough
  parallel capability ownership. Use `setup-rust-workstreams` if substrate is missing, then
  `$dev-flow` / `open-workstream`.
- **Large repo**: stable capability areas, multiple crates, multiple terminals or worktrees, and
  durable subsystem boundaries. Use `setup-rust-workstreams` with architecture maps, then
  `run-architecture-lane` for lane terminals and `coordinate-workstream` for planner control.
- **Legacy substrate**: old workstream docs exist but miss lane refs, task-ledger fields, evidence
  gates, or current repo rules. Repair docs through `setup-rust-workstreams`; preserve ADRs and
  local policy.

Choose the smallest workflow scale that protects traceability and reduces coordination cost.

## Route

- Missing `AGENTS.md`, `CONTEXT.md`, or `docs/workstreams/` -> `setup-rust-workstreams`.
- Unclear product terms, lane boundaries, non-goals, or risk -> `grill-with-docs`.
- Existing docs need architecture-lane repair -> `setup-rust-workstreams`, then `$dev-flow`.
- Large capability lane ready for a terminal -> `run-architecture-lane`.
- Multiple lane terminals or worker terminals active -> `coordinate-workstream`.
- Structure needs review before splitting work -> `improve-codebase-architecture`.
- Confirmed boundary/deletion refactor -> `fearless-refactor`.
- Normal development after classification -> `$dev-flow`.

## Repair Rules

- Preserve existing ADRs, project language, and repo rules.
- Add missing sections instead of replacing user docs.
- Promote durable knowledge from old journals or handoffs into ADRs, architecture docs, or
  workstream docs only when evidence supports it.
- Do not make every project multi-agent. For small repos, keep the workflow light.
- Do not set a Codex goal for the audit or for an architecture lane. Recommend a goal only for one
  bounded task after a workstream task ledger exists.

## Output

Report:

- scale classification and confidence,
- existing workflow substrate status,
- whether architecture lanes are useful or overkill,
- recommended user-facing skill to call next,
- docs to repair or initialize,
- planner / lane / worker terminal shape if parallelism is justified,
- and risks that should be grilled before docs change.

## Example

```text
Use $audit-project-scale on this Rust repo. Decide whether it should stay on a small $dev-flow path,
use normal workstreams, or add architecture lanes and a planner terminal. Repair old workflow docs
only by delegating to the right setup or grill skill.
```

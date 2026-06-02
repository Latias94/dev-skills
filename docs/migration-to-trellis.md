# Migration To Trellis

This repository retired its Rust workstream workflow. Use Trellis beta as the active workflow system
and keep this repository as a small helper-skill collection.

## What To Keep

- ADRs and architecture docs in target projects.
- Stable repo rules from `AGENTS.md` or `CLAUDE.md`.
- Domain vocabulary and invariants from `CONTEXT.md`, distilled into `.trellis/spec/guides/`.
- Validation commands that should become Trellis quality checks.

## What To Convert

- Only currently active workstreams that still represent live work.
- Convert each into one Trellis task, or one parent task with explicit subtasks.
- Use legacy `DESIGN.md`, `TODO.md`, `HANDOFF.md`, or `EVIDENCE_AND_GATES.md` only as PRD/research
  input.

## What To Retire

- Closed, completed, abandoned, or stale workstream directories.
- `WORKSTREAM.json`, `TASKS.jsonl`, and `CAMPAIGNS.jsonl` as active state.
- Planner runtime output and hook experiments from the retired workflow.

## Audit Command

```powershell
python skills\engineering\migrate-to-trellis\scripts\audit_trellis_migration.py <repo> --format text
```

The audit is read-only. It should be run before deleting legacy workflow files from a target repo.

## Trellis Context Rule

`implement.jsonl` and `check.jsonl` should reference Trellis specs and task research, not source-code
file lists. Implement/check agents should discover source files from the PRD, specs, and repo
inspection.

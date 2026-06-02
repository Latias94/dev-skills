# Scenario NAKO-001 — Routing Audit

## Prompt

Use `dev-skills` to inspect this repo, identify active lanes or workstreams, and recommend the next
safe task.

## Repo

- `repo-ref/nako`

## Expected Route

- `audit-project-scale` or planner-aware discovery
- read-only inspection first
- read `AGENTS.md`, `CONTEXT.md`, `docs/architecture/LANES.md`, and active workstreams
- no code changes
- no bootstrap attempt

## Why This Scenario Matters

`nako` is already a large Rust program with:

- architecture lane docs,
- many durable workstreams,
- targeted validation scripts,
- mixed product surfaces.

If `dev-skills` cannot route this repo correctly, the upper-planner story is not credible.

## Expected Success Signals

- recognizes repo scale as large
- treats existing workstream substrate as authoritative
- distinguishes lane/program work from a direct task
- recommends a bounded next action rather than vague “ask the user what next”

## Expected Failure Signals

- recommends `setup-rust-workstreams`
- ignores `docs/architecture/LANES.md`
- proposes immediate implementation without inspecting readiness
- opens a new workstream despite obvious existing active queues

## Baseline Observation

Read-only inspection already shows:

- root `AGENTS.md`
- root `CONTEXT.md`
- `docs/architecture/LANES.md`
- multiple `docs/workstreams/*`
- focused `cargo nextest run` validation commands

Therefore the scenario should start above bootstrap level.

## Preliminary Rating

- Routing: `2` if planner-aware read-only discovery is chosen
- Artifact Integrity: pending
- Execution Quality: pending
- Operator Cost: pending

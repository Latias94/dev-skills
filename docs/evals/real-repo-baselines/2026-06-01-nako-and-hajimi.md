# Real Repo Baselines — 2026-06-01

## Purpose

This file records the first read-only baseline after cloning:

- `repo-ref/nako`
- `repo-ref/hajimi`

The purpose is to ground `dev-skills` refactors in real repository evidence instead of generic
workflow theory.

## Baseline: Nako

Repo:

- `repo-ref/nako`

Observed traits:

- large Rust workspace with multiple surfaces: crates, web, Tauri, Android, deployment assets,
  SDKs
- has `AGENTS.md`, `CONTEXT.md`, `PRODUCT.md`, `DESIGN.md`
- has `docs/architecture/LANES.md` and multiple architecture lane docs
- has `docs/workstreams/`
- validation scripts explicitly use focused `cargo nextest run` commands and workspace-level gates

Immediate implication for `dev-skills`:

- this is a genuine lane/program candidate repo
- `audit-project-scale` should not classify this as a direct-task-first repository without reading
  architecture docs and active workstreams
- `plan-engineering-program` is a valid top-level path when the user asks for global coordination
- `resume-workstream` should work well because the substrate already exists

Key risk to validate:

- whether the current `dev-skills` routing is sharp enough to avoid over-ceremony when the user only
  wants one bounded task inside this large repo

## Baseline: Hajimi

Repo:

- `repo-ref/hajimi`

Observed traits:

- Rust workspace with strong ADR coverage
- many durable workstreams under `docs/workstreams/`
- explicit `AGENTS.md` guidance already aligned with ADR + workstream authority
- focused package and workspace validation commands using `cargo nextest run`
- several workstreams already contain closeout-quality evidence structure

Immediate implication for `dev-skills`:

- this repo is an excellent validation target for orchestration quality
- many of the patterns `dev-skills` wants to encourage already exist here
- failure modes are more likely to be runtime ambiguity and workflow friction than missing substrate

Key risk to validate:

- whether `dev-skills` can correctly determine readiness and next-step routing from existing
  workstream state instead of asking the operator to restate context

## First Evaluation Expectations

### Nako expectation

If asked to inspect the repo and propose next work:

- the system should route through planner-aware discovery,
- read architecture + active workstream artifacts first,
- and avoid code changes.

### Hajimi expectation

If asked to inspect current workstreams and decide assignability:

- the system should identify active queues and gates from existing artifacts,
- distinguish ready work from historical closed work,
- and state a bounded implementation horizon.

## Refactor Signal From This Baseline

The baselines reinforce one central conclusion:

- `dev-skills` does not need more abstract workflow concepts first.
- it needs a stronger runtime bridge from existing artifacts to current-turn execution guidance.

That means the next refactor steps should prioritize:

1. clearer runtime phase/breadcrumb output,
2. stronger artifact drift checks,
3. better real-repo scenario validation,
4. and tighter control over when heavy workflow machinery is actually invoked.

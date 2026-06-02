# Dev Skills Next Iteration Backlog

## Purpose

This backlog records the highest-value next steps after the current readiness/audit refactor pass.
It is intentionally short and ordered.

Use it as the next resumption point instead of restarting from broad comparison work.

## Done In This Iteration

These items are now materially true in the repository:

1. `dev-skills` explicitly distinguishes `READINESS` and `AUDIT`.
2. `program_status.py` reports:
   - `operating_mode`
   - `operating_reason`
   - `implementation_horizon`
3. `validate_orchestration_state.py` catches more real historical evidence drift.
4. `dev-flow`, planner, lane, resume, integrator, README, workflow, and usage docs now use the
   same mode/horizon vocabulary.
5. `repo-ref/nako` and `repo-ref/hajimi` have been used as real reference repositories.

## Highest-Value Next Steps

### 1. Add a dedicated audit summary mode or script

Why first:

- `hajimi` proves historical-only repos need an audit-native summary
- current planner language is much better, but still piggybacks on readiness-oriented scripts

Success looks like:

- a read-only audit report focused on historical drift,
- separate from assignment readiness,
- with cleanup recommendations grouped by pattern instead of one warning per workstream.

### 2. Run a richer planner-style `nako` exercise

Why second:

- `nako` currently has one active ready workstream and is the best route-choice benchmark
- current rehearsal notes are script-backed, but not yet a richer planner narrative

Success looks like:

- one documented example showing how `plan-engineering-program` should answer on `nako`,
- including current phase, operating mode, horizon, recommended next route, and why.

### 3. Decide whether evidence normalization is a product goal

Why third:

- both `nako` and `hajimi` expose many historical workstreams without normalized task terminal
  evidence in `WORKSTREAM.json`
- this is useful audit information, but not automatically worth forcing into every repo

Decision needed:

- should `dev-skills` push users toward evidence normalization campaigns,
- or should it treat this as optional historical hygiene?

### 4. Consider a machine-readable planner breadcrumb artifact

Why fourth:

- runtime language is now clearer,
- but planner state is still spread across docs, scripts, and prompt conventions

Status:

- partially done: `planner_breadcrumb.py` now provides a derived read-only runtime snapshot from
  existing artifacts
- still open: decide whether this should stay script-only or gain a stronger local runtime contract

Success looks like:

- a minimal artifact or derived state view that records current phase/mode/horizon safely,
- without becoming a competing source of truth.

## Deprioritized For Now

These are explicitly not the next thing:

- replacing ADR/workstream truth with a Trellis-like workflow source of truth,
- adding more workstream abstractions,
- making medium work more ceremonial,
- expanding validation until historical repos are red by default.

## Resume Hint

If resuming later, start by reading:

1. `docs/evals/results/2026-06-02-nako-hajimi-findings.md`
2. `docs/evals/results/2026-06-02-planner-rehearsal-notes.md`
3. `docs/roadmaps/dev-skills-refactor-roadmap.md`
4. this backlog file

Then choose whether the next action is:

- `AUDIT` deepening,
- `nako` planner rehearsal,
- or evidence-normalization policy design.

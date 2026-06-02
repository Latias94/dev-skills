# Nako And Hajimi Findings — 2026-06-02

## Scope

This note records what the current `dev-skills` scripts and contracts revealed when pointed at:

- `repo-ref/nako`
- `repo-ref/hajimi`

It is not a final evaluation. It is a checkpoint used to prioritize the next refactors.

## Finding 1: `READINESS` and `AUDIT` must stay separate

This is the clearest conclusion so far.

### Evidence

- `repo-ref/nako` contains one active ready workstream and many historical ones.
- `repo-ref/hajimi` currently presents as historical-only in `program_status.py`.
- the enhanced validation script finds many historical evidence gaps in both repos.

### Implication

Historical evidence drift is common even in strong repos.
If `dev-skills` treats that drift as an assignment blocker by default, it will regularly report the
wrong next move.

### Action taken

- `orchestration-runtime.md` now defines `READINESS` vs `AUDIT`
- orchestrator skills now reference the distinction
- `program_status.py` now reports `operating_mode` and `operating_reason`

## Finding 2: Historical repos still need useful planner summaries

### Evidence

Running `program_status.py` on `repo-ref/hajimi` previously yielded a correct but shallow result:

- `implementation_horizon = 0`
- many historical workstreams
- no explanation of whether that meant “nothing assignable” or “this is an audit baseline”

### Implication

Upper-planner output needs to explain zero horizon. Otherwise the user cannot tell whether:

- the active queue is broken,
- the repo is idle,
- or the planner is looking at history only.

### Action taken

`program_status.py` now reports:

- `operating_mode`
- `operating_reason`
- `implementation_horizon`

## Finding 3: Workstream evidence quality is not uniform across mature repos

### Evidence

The enhanced orchestration validator found recurring patterns in both repos:

- TODO tasks not mirrored by terminal evidence in `WORKSTREAM.json`
- gate evidence commands not always mirrored literally in `gates`
- historical closeouts often good enough for humans but not normalized enough for strict machine checks

### Implication

`dev-skills` needs a layered validation model:

1. strict active-queue readiness checks,
2. softer historical audit checks,
3. optional cleanup campaigns for evidence normalization.

This should not be modeled as one red/green gate.

## Finding 4: `nako` is the better near-term route-choice benchmark

### Evidence

`repo-ref/nako` currently exposes:

- one active ready workstream,
- many historical workstreams,
- explicit lane docs,
- multi-surface product complexity.

### Implication

This repo is ideal for testing:

- whether `audit-project-scale` escalates correctly,
- whether `plan-engineering-program` can propose the next safe move,
- whether `resume-workstream` lands on a bounded next task instead of reopening planning unnecessarily.

## Finding 5: `hajimi` is the better historical-audit benchmark

### Evidence

`repo-ref/hajimi` currently reads as:

- rich ADR/workstream substrate,
- large historical corpus,
- few or no active rows in the current snapshot.

### Implication

This repo is ideal for testing:

- audit-mode output,
- historical drift inspection,
- and whether `dev-skills` can explain “nothing currently assignable” without sounding confused.

## Next Refactor Priorities

1. Teach more user-facing outputs to surface:
   - current phase,
   - operating mode,
   - implementation horizon,
   - active blockers vs historical findings.
2. Add a dedicated audit-oriented summary script or script mode.
3. Run a read-only planner-style scenario against `nako` and capture the resulting route recommendation.
4. Decide whether readiness scripts should learn more from `WORKSTREAM.json.evidence`, or whether
   evidence normalization should remain a follow-on cleanup concern.

## Update After Breadcrumb Prototype

A derived runtime snapshot now exists via
`skills/engineering/plan-engineering-program/scripts/planner_breadcrumb.py`.

Observed value:

- `nako` now yields a compact `ASSIGN` breadcrumb with active workstream, active task, active
  campaign, and required context.
- `hajimi` now yields a compact `AUDIT`/`DISCOVERY` breadcrumb instead of a generic zero-horizon
  summary.

Implication:

- the next iteration should treat runtime hardening as a derivation problem from existing artifacts,
  not as a new authoritative workflow layer.

## Update After Prompt-Ready Runtime Block

The breadcrumb prototype is now usable as a prompt-ready runtime bridge:

- `python skills/engineering/plan-engineering-program/scripts/planner_breadcrumb.py <repo> --format prompt`

Observed value:

- planner-style turns can now be prefixed with a compact `<planner-runtime>` block instead of
  re-reading a wide workstream inventory every time
- the block is explicit about phase, mode, horizon, active unit, blockers, context, and next step
- the block also states that it is derived guidance only, reducing the risk that it becomes a
  second authority layer

Remaining gap:

- this is still manually consumable runtime hardening, not automatic per-turn injection
- subagent-specific context loading is still much softer than Trellis

Next implication:

- the next meaningful experiment is not another broad analysis pass
- it is a live prompt-consumption rehearsal comparing planner outputs with and without the derived
  runtime block on the same real-repo scenarios

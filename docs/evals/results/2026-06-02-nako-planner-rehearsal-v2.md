# Nako Planner Rehearsal V2 — 2026-06-02

## Purpose

This note upgrades the earlier script-backed rehearsal into a more realistic upper-planner answer.

The target question is:

- can `dev-skills` now produce an answer that feels like a real orchestration recommendation, not
  just raw script output?

## Evidence Read

- `program_status.py repo-ref/nako`
- `planner_breadcrumb.py repo-ref/nako`
- `validate_orchestration_state.py repo-ref/nako --format json`
- `audit_summary.py repo-ref/nako`
- `planner_payload.py repo-ref/nako`
- existing baseline and findings notes

## Observed Runtime Signal

- `Operating Mode: READINESS`
- `Implementation Horizon: 1`
- `Phase: ASSIGN`
- active workstream:
  `generated-artifact-bulk-metadata-apply`
- active task:
  `GABMA-020`
- active campaign:
  `GABMA-20260601-01`
- active lane:
  `library-metadata-control-plane`

Required context derived by breadcrumb:

- `CONTEXT.md`
- `docs/workstreams/generated-artifact-metadata-authority-apply/README.md`
- `docs/workstreams/generated-artifact-metadata-authority-apply/CLOSEOUT.md`
- `docs/workstreams/generated-artifact-metadata-authority-apply/HANDOFF.md`
- `docs/workstreams/web-admin-generated-artifact-review-mutations/ROUTE_API_READINESS.md`
- `docs/workstreams/metadata-application-policy-seam/`
- `docs/workstreams/metadata-application-cross-path-audit/`
- `docs/architecture/LIBRARY_PIPELINE.md`

Historical audit pressure:

- `audit_summary.py` reports 177 historical warnings
- all current warnings collapse into one dominant pattern:
  `missing_terminal_task_evidence`

## Rehearsed Planner Answer

```md
## Program Action
Mode: ASSIGN
Operating Mode: READINESS
Implementation Horizon: 1
Now: resume the active metadata-control-plane queue by assigning `GABMA-020`
Why: the repo has one active ready workstream with explicit current task, campaign, and context;
historical audit drift exists but does not affect active-queue readiness
```

Recommended action:

- do not reopen repo-scale audit
- do not reopen broad architecture planning
- do not spawn parallel workers yet unless the current workstream docs expose an independently
  validatable disjoint slice beyond `GABMA-020`
- route either to:
  - `resume-workstream` when the operator wants bounded continuation from current artifacts, or
  - `run-workstream-task` when `GABMA-020` is already sufficiently scoped in the task ledger

Safe immediate user-facing recommendation:

- “This repo is in `READINESS`, not bootstrap or audit-only mode. The next safe move is to resume
  `generated-artifact-bulk-metadata-apply` and execute `GABMA-020` inside the
  `library-metadata-control-plane` lane. Historical evidence drift exists across older workstreams,
  but it is audit noise, not an active-queue blocker.”

## Why This Is Better Than The First Rehearsal

The first rehearsal proved the vocabulary.
This one proves the runtime bridge is tighter:

- `program_status.py` tells us whether work is assignable
- `planner_breadcrumb.py` tells us what the current live unit actually is
- `audit_summary.py` prevents historical warnings from overwhelming the planner answer

That combination is much closer to the Trellis advantage we actually want:

- stronger per-turn runtime clarity,
- without moving authority out of project-owned docs.

The newest addition, `planner_payload.py`, now packages that combination into one read-only planner
answer instead of requiring the operator or prompt to merge multiple script outputs manually.

## Remaining Gaps

1. The planner still infers “assign `GABMA-020`” from current-task state, not from richer task
   utility ranking.
2. There is still no single read-only script that combines readiness, breadcrumb, and audit summary
   into one planner payload.
3. Medium-task ceremony still needs more real-repo testing beyond large program cases.

## Conclusion

`dev-skills` now supports a credible large-repo planner answer on `nako`.

That is strong evidence that the right next refactors are:

- better aggregation and presentation,
- not a redesign of the authority model.

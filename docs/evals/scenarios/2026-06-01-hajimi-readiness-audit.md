# Scenario HAJIMI-002 — Readiness Audit

## Prompt

Use `dev-skills` to inspect current workstreams and decide whether any bounded implementation work is
actually assignable right now.

## Repo

- `repo-ref/hajimi`

## Expected Route

- `plan-engineering-program` or equivalent planner-aware inspection
- read `AGENTS.md`, `CONTEXT.md`, relevant ADRs, active workstreams
- determine implementation horizon from artifact state
- stay read-only

## Why This Scenario Matters

`hajimi` already contains:

- strong ADR coverage,
- many workstreams,
- evidence-rich closeouts,
- targeted and workspace-wide validation gates.

That makes it ideal for checking whether `dev-skills` can infer readiness from real artifacts instead
of demanding operator restatement.

## Expected Success Signals

- distinguishes active queues from historical closed work
- identifies missing runtime artifacts or drift when present
- reports a bounded implementation horizon
- names concrete blockers when work is not assignable

## Expected Failure Signals

- treats all historical workstreams as active queue
- assumes assignability without checking gates or context manifests
- asks generic “what next?” despite sufficient repo evidence
- conflates planner work with worker execution

## Baseline Observation

Read-only inspection already shows:

- root `AGENTS.md`
- root `CONTEXT.md`
- many ADRs under `docs/adr/`
- many workstreams under `docs/workstreams/`
- several closed workstreams with strong evidence payloads

This repo should strongly pressure-test readiness logic, not bootstrap logic.

## Preliminary Rating

- Routing: `2` if planner-aware readiness inspection is chosen
- Artifact Integrity: pending
- Execution Quality: pending
- Operator Cost: pending

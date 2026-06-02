# Dispatch Rehearsal Notes — 2026-06-02

## Purpose

This note records the first read-only dispatch rehearsal built on top of `planner_payload.py`.

The goal is to answer a more operational question than earlier planner rehearsals:

- if the upper planner had to decide whether to launch a worker right now, what should it do?

## Nako

Evidence:

- `planner_payload.py repo-ref/nako`
- `dispatch_rehearsal.py repo-ref/nako`

Observed answer:

- `Mode: ASSIGN`
- `Operating Mode: READINESS`
- `Implementation Horizon: 1`
- recommended route:
  `run-workstream-task`
- parallelism:
  `False`
- reason:
  only one ready active unit is derived from current artifacts

Value:

- the system now produces a bounded worker prompt draft for `GABMA-020`
- the prompt includes required context, result marker, stop conditions, and the explicit ban on
  choosing the global next task

Interpretation:

- this is the first point where the planner stack feels ready to drive a real worker terminal
  without relying on the operator to manually synthesize route + context + stop conditions

## Hajimi

Evidence:

- `planner_payload.py repo-ref/hajimi`
- `dispatch_rehearsal.py repo-ref/hajimi`

Observed answer:

- `Mode: DISCOVERY`
- `Operating Mode: AUDIT`
- `Implementation Horizon: 0`
- recommended route:
  `plan-engineering-program`
- no worker prompt
- parallelism:
  `False`

Value:

- the system explicitly refuses fabricated worker dispatch on a historical-only repo snapshot
- this is the correct behavior and a meaningful improvement over systems that would launch a worker
  just because “some workstreams exist”

## Conclusion

`dispatch_rehearsal.py` is now a useful pre-dispatch baseline:

- on `nako`, it recommends a real bounded worker route
- on `hajimi`, it correctly blocks worker dispatch and keeps the planner in audit mode

This is strong evidence that the next stage should be live subagent experiments, not more abstract
workflow theory.

Follow-on:

- `handoff_chain_rehearsal.py` now extends this into a full read-only planner -> worker -> review
  -> verify -> integrate chain rehearsal

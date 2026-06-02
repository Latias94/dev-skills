# Live Experiment Playbook — 2026-06-02

## Purpose

This playbook defines the next practical experiment for `dev-skills`.

The infrastructure now exists to derive:

- readiness
- runtime breadcrumb
- audit summary
- unified planner payload
- dispatch rehearsal
- full handoff-chain rehearsal

The next step is to stop proving the theory and run a real bounded multi-role experiment.

## Target Repositories

### Primary execution target

- `repo-ref/nako`

Reason:

- one active ready workstream exists
- current evidence supports a bounded real execution chain
- historical drift exists, which makes the experiment realistic

### Primary refusal target

- `repo-ref/hajimi`

Reason:

- current snapshot is historical-heavy
- the correct behavior is to refuse fabricated execution

## Preflight Commands

Run these before launching any live worker terminal:

```powershell
python skills\engineering\plan-engineering-program\scripts\program_status.py repo-ref\nako
python skills\engineering\plan-engineering-program\scripts\planner_payload.py repo-ref\nako
python skills\engineering\plan-engineering-program\scripts\dispatch_rehearsal.py repo-ref\nako
python skills\engineering\plan-engineering-program\scripts\handoff_chain_rehearsal.py repo-ref\nako
```

For the refusal baseline:

```powershell
python skills\engineering\plan-engineering-program\scripts\program_status.py repo-ref\hajimi
python skills\engineering\plan-engineering-program\scripts\planner_payload.py repo-ref\hajimi
python skills\engineering\plan-engineering-program\scripts\dispatch_rehearsal.py repo-ref\hajimi
python skills\engineering\plan-engineering-program\scripts\handoff_chain_rehearsal.py repo-ref\hajimi
```

## Entry Criteria

Proceed with a live `nako` experiment only when all are true:

- `Operating Mode: READINESS`
- `Implementation Horizon: 1+`
- `dispatch_rehearsal.py` recommends a real worker route
- `handoff_chain_rehearsal.py` reports `execution_chain_ready`

Do not proceed when:

- `Operating Mode: AUDIT`
- `Implementation Horizon: 0`
- recommended route stays at planner level
- `handoff_chain_rehearsal.py` reports `planner_only`

## Live Nako Experiment Shape

1. Planner terminal:
   - use `planner_payload.py` as pre-dispatch baseline
   - confirm active unit and stop conditions
2. Worker terminal:
   - use the derived worker prompt for the current task
3. Review terminal:
   - review the worker result against workstream contract and current diff
4. Verify terminal:
   - run fresh gates for the exact claim
5. Integrator terminal:
   - accept or reject based on repo evidence and result markers

## What To Observe

### Positive signals

- prompts do not need major manual repair before use
- required context list is sufficient
- stop conditions are concrete and actionable
- worker scope remains bounded
- review/verify/integrate prompts line up with the same task and workstream
- the chain survives without introducing new authority files

### Negative signals

- planner still needs manual synthesis of missing route data
- worker prompt lacks scope, validation, or result-marker clarity
- review/verify prompts drift from the same task/workstream
- integrator still needs chat as primary evidence
- historical drift overwhelms the active execution chain

## Hajimi Refusal Experiment

The `hajimi` experiment is successful if the planner refuses live execution cleanly.

Success signals:

- no worker prompt is produced
- no fake review/verify chain is produced
- refusal is grounded in current repo state
- the recommended next move stays in audit or new-workstream planning

Failure signals:

- a worker prompt is produced anyway
- historical workstreams are misread as active assignments
- the planner uses vague language instead of a specific refusal condition

## Decision Rule

If `nako` preflight remains clean and `hajimi` refusal remains clean, the next session should run a
real bounded multi-terminal experiment on `nako`.

If either side regresses, fix the derivation layer first instead of forcing a live run.

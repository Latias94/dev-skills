# Nako Live Runbook — 2026-06-02

## Purpose

This runbook is the immediate next step after the current read-only rehearsals.

It is designed so the next session can run a real bounded `nako` experiment without manually
reconstructing planner state, worker scope, or review/verify/integrate prompts.

## Current Preflight State

As of this snapshot:

- `Operating Mode: READINESS`
- `Implementation Horizon: 1`
- active workstream:
  `generated-artifact-bulk-metadata-apply`
- active task:
  `GABMA-020`
- active campaign:
  `GABMA-20260601-01`
- lane:
  `library-metadata-control-plane`
- chain state:
  `execution_chain_ready`

Historical audit pressure exists:

- `missing_terminal_task_evidence x177`

but it is currently not an active-queue blocker.

## Preflight Commands

Run these first and stop if their shape materially changes:

```powershell
python skills\engineering\plan-engineering-program\scripts\program_status.py repo-ref\nako
python skills\engineering\plan-engineering-program\scripts\planner_payload.py repo-ref\nako
python skills\engineering\plan-engineering-program\scripts\dispatch_rehearsal.py repo-ref\nako
python skills\engineering\plan-engineering-program\scripts\handoff_chain_rehearsal.py repo-ref\nako
```

Proceed only if all remain true:

- `Operating Mode: READINESS`
- `Implementation Horizon: 1`
- recommended route is `run-workstream-task`
- handoff chain state is `execution_chain_ready`

## Terminal Layout

Use a minimal five-role layout:

1. Planner / commander
2. Worker
3. Reviewer
4. Verifier
5. Integrator

Do not add parallel workers in this run. The current state derives only one ready active unit.

## Planner Prompt

Paste into the planner terminal:

```text
Use $plan-engineering-program for repo-ref/nako.
Treat the current derived payload and handoff-chain rehearsal as the pre-dispatch baseline.
Confirm whether GABMA-020 in generated-artifact-bulk-metadata-apply is still the next safe bounded
task.
If yes, hand off to a worker/reviewer/verifier/integrator chain without reopening global planning.
If no, explain exactly what active-queue fact changed and stop before worker dispatch.
```

Success signals:

- planner stays in `ASSIGN`
- planner keeps scope on `GABMA-020`
- planner does not reopen broad repo planning

Failure signals:

- planner forgets the active unit
- planner widens into unrelated lanes
- planner ignores active-queue facts and asks “what next?”

## Worker Prompt

Paste into the worker terminal:

```text
Use $run-workstream-task to execute task GABMA-020.
You are not alone in the codebase.
Role: worker
Program state: ASSIGN
Task or campaign: GABMA-020 / GABMA-20260601-01
Owned scope: infer from TASKS.jsonl and workstream ledger before editing
Forbidden/shared scope: any scope not explicitly owned by the assigned task
Required context:
- CONTEXT.md
- docs/workstreams/generated-artifact-metadata-authority-apply/README.md
- docs/workstreams/generated-artifact-metadata-authority-apply/CLOSEOUT.md
- docs/workstreams/generated-artifact-metadata-authority-apply/HANDOFF.md
- docs/workstreams/web-admin-generated-artifact-review-mutations/ROUTE_API_READINESS.md
- docs/workstreams/metadata-application-policy-seam/
- docs/workstreams/metadata-application-cross-path-audit/
- docs/architecture/LIBRARY_PIPELINE.md
Validation: use the task-local validation command from TASKS.jsonl
Stop conditions: shared-scope drift, ADR/schema/public-contract change, failed gates, missing context
Side-effect policy: do not infer beyond current campaign/workstream approval
Result marker: WORKSTREAM_RESULT:
Return path: upper planner or integrator for review/verify and next approved task
Known blockers before dispatch: none
Do not choose the global next task.
```

Success signals:

- worker stays within task scope
- worker returns a valid `WORKSTREAM_RESULT:`
- worker does not invent global reprioritization

Failure signals:

- worker expands scope without justification
- worker omits result marker
- worker cannot find enough context despite provided manifest

## Review Prompt

Paste into the reviewer terminal:

```text
Use $review-workstream to review task GABMA-020 in docs/workstreams/generated-artifact-bulk-metadata-apply
against the workstream contract, changed file scope, and current diff.
End with a REVIEW_RESULT: marker.
```

Success signals:

- review comments are grounded in task/workstream contract
- returns a valid `REVIEW_RESULT:`

Failure signals:

- review drifts away from the same task
- review cannot identify scope from repo evidence

## Verify Prompt

Paste into the verifier terminal:

```text
Use $verify-rust-workstream to verify task GABMA-020 in docs/workstreams/generated-artifact-bulk-metadata-apply
with fresh command evidence before integration.
End with a VERIFY_RESULT: marker.
```

Success signals:

- uses fresh commands
- updates evidence path
- returns a valid `VERIFY_RESULT:`

Failure signals:

- relies on worker claims instead of commands
- skips critical gates without reason

## Integrator Prompt

Paste into the integrator terminal:

```text
Use $integrate-lane-results after worker, review, and verify reports for task GABMA-020 in
docs/workstreams/generated-artifact-bulk-metadata-apply.
Reconstruct the result from repo evidence first, then classify it with an INTEGRATION_RESULT: marker.
```

Success signals:

- integrator reconstructs from repo evidence before asking for chat
- returns a valid `INTEGRATION_RESULT:`
- correctly routes accept / needs-fix / blocked-decision

Failure signals:

- integrator accepts plain prose `DONE`
- integrator needs chat as primary evidence path

## What To Record

During the live run, capture:

- whether each prompt needed manual repair
- whether each role stayed on the same task/workstream
- whether result markers were produced correctly
- whether review and verify used the same scope as worker output
- whether integrator could classify from repo evidence
- whether any stop condition fired

## Interpretation Rule

If the run fails, classify the failure source:

- **workflow derivation issue**:
  missing context, missing stop conditions, prompt drift, missing role contract
- **repo substrate issue**:
  task ledger drift, unclear scope in current workstream, missing validation, stale handoff
- **model execution issue**:
  prompt was adequate but the role ignored it

Do not immediately “fix the skill” when the repo substrate is the actual problem.

## Next Decision

After the run:

- if the chain stays aligned, move to a broader same-lane experiment
- if the chain fails at one role, tighten that role's prompt or supporting derivation layer
- if the chain fails because `nako` substrate is still too soft, record the missing artifact and
  keep the experiment bounded rather than reopening architecture globally

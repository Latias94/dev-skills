# Nako Live Preflight Record — 2026-06-02

## Scope

This record is the first bounded-chain live preflight for `repo-ref/nako`.

It is not a code-change run.
It only captures the current dispatch baseline for a real planner/worker chain using repeatable
local commands and current repo truth.

## Preflight Snapshot

Verified on 2026-06-02 from `F:\SourceCodes\Github\dev-skills` with:

```powershell
python skills\engineering\plan-engineering-program\scripts\program_status.py repo-ref\nako
python skills\engineering\plan-engineering-program\scripts\planner_hook_adapter.py repo-ref\nako --prompt "Run the next safe bounded chain experiment for this repo." --format json
python skills\engineering\plan-engineering-program\scripts\inject_planner_runtime.py repo-ref\nako --debug
```

Observed state:

- repo: `repo-ref/nako`
- branch: `main`
- head: `baa3c796`
- worktrees: `1`
- operating mode: `READINESS`
- implementation horizon: `1`
- ready active workstreams: `1`
- active workstream: `generated-artifact-bulk-metadata-apply`
- active lane: `library-metadata-control-plane`
- active task: `GABMA-020`
- approved campaign: `GABMA-20260601-01`

`program_status.py`, `planner_hook_adapter.py`, and `inject_planner_runtime.py --debug` currently
agree on the same active unit.
This is the minimum condition for a bounded live chain start.

## Installed Hook Verification

Installed file:

- `repo-ref/nako/.codex/hooks.json`

Installed command target:

```text
python -X utf8 skills/engineering/plan-engineering-program/scripts/inject_planner_runtime.py
```

Verification result after install:

- emitted event:
  `UserPromptSubmit`
- emitted mode:
  `READINESS`
- emitted horizon:
  `1`
- emitted route:
  `run-workstream-task`
- emitted active unit:
  `generated-artifact-bulk-metadata-apply / GABMA-020 / GABMA-20260601-01`

## Active Unit

Authoritative workstream state comes from:

- `repo-ref/nako/docs/workstreams/generated-artifact-bulk-metadata-apply/WORKSTREAM.json`
- `repo-ref/nako/docs/workstreams/generated-artifact-bulk-metadata-apply/TASKS.jsonl`
- `repo-ref/nako/docs/workstreams/generated-artifact-bulk-metadata-apply/CAMPAIGNS.jsonl`
- `repo-ref/nako/docs/workstreams/generated-artifact-bulk-metadata-apply/HANDOFF.md`

Current active unit:

- workstream: `generated-artifact-bulk-metadata-apply`
- task: `GABMA-020`
- campaign: `GABMA-20260601-01`

## Planner / Worker Chain Start

This preflight supports a bounded chain starting at:

- planner entry: `plan-engineering-program`
- execution route: `run-workstream-task`
- first worker scope: `GABMA-020`
- chain shape: `planner -> worker -> reviewer -> verifier -> integrator`

Derived planner runtime currently says:

- phase: `ASSIGN`
- safe next move: `assignment`
- recommended route: `run-workstream-task`
- route reason: `ready bounded task exists`

This means the planner should not reopen global planning unless repo evidence contradicts the
current queue.

## Required Context At Dispatch

The current derived prompt prelude identifies this required context set:

- `CONTEXT.md`
- `docs/workstreams/generated-artifact-metadata-authority-apply/README.md`
- `docs/workstreams/generated-artifact-metadata-authority-apply/CLOSEOUT.md`
- `docs/workstreams/generated-artifact-metadata-authority-apply/HANDOFF.md`
- `docs/workstreams/web-admin-generated-artifact-review-mutations/ROUTE_API_READINESS.md`
- `docs/workstreams/metadata-application-policy-seam/`
- `docs/workstreams/metadata-application-cross-path-audit/`
- `docs/architecture/LIBRARY_PIPELINE.md`

## Success Signals

Treat the live preflight as successful if all remain true before worker dispatch:

- `program_status.py` still reports `Operating Mode: READINESS`
- `program_status.py` still reports `Implementation Horizon: 1`
- the only ready active workstream remains `generated-artifact-bulk-metadata-apply`
- `planner_hook_adapter.py` still recommends `run-workstream-task`
- `inject_planner_runtime.py --debug` still reports the same active unit
- planner remains in bounded assignment mode and does not widen into unrelated lanes

## Failure Signals

Treat the preflight as failed and stop before worker dispatch if any of these occur:

- `program_status.py` no longer reports `READINESS`
- implementation horizon is no longer `1`
- the active workstream or current task changes away from
  `generated-artifact-bulk-metadata-apply / GABMA-020`
- `planner_hook_adapter.py` no longer recommends `run-workstream-task`
- required context can no longer be resolved from repo truth
- planner tries to choose a different global next task without repo evidence

## Immediate Next Command Set

Before a real live chain run, rerun exactly:

```powershell
python skills\engineering\plan-engineering-program\scripts\program_status.py repo-ref\nako
python skills\engineering\plan-engineering-program\scripts\planner_payload.py repo-ref\nako
python skills\engineering\plan-engineering-program\scripts\dispatch_rehearsal.py repo-ref\nako
python skills\engineering\plan-engineering-program\scripts\handoff_chain_rehearsal.py repo-ref\nako
python skills\engineering\plan-engineering-program\scripts\planner_hook_adapter.py repo-ref\nako --prompt "Run the next safe bounded chain experiment for this repo." --format json
```

Proceed only if the first and last commands still align on:

- `READINESS`
- horizon `1`
- active unit `generated-artifact-bulk-metadata-apply / GABMA-020`
- bounded execution route `run-workstream-task`

## Interpretation

This preflight does not prove the chain will execute well.
It proves only that the current repo truth and current dev-skills derivation still align tightly
enough to justify a first bounded live planner/worker run without reopening architecture planning.

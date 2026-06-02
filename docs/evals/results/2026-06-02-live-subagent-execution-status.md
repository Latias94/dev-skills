# Live Subagent Execution Status — 2026-06-02

## Goal

Track which real-repo experiments are ready to run immediately with actual subagents, and which
ones still need substrate or tooling work first.

## Current Matrix Status

| Repo | Expected posture | Current status | Immediate readiness | Notes |
| --- | --- | --- | --- | --- |
| `repo-ref/hajimi` | planner refusal | `AUDIT`, horizon `0` | ready | best first live control case |
| `repo-ref/nako` | planner -> worker -> review -> verify -> integrate | `READINESS`, horizon `1` | ready | bounded chain target is `GABMA-020` |
| `repo-ref/skills` | medium direct/downshift | `READINESS`, no workstreams | partial | valid for restraint/downshift, not for full chain |

## Verified Preflight Snapshot

### `repo-ref/hajimi`

Verified with:

```powershell
python skills\engineering\plan-engineering-program\scripts\program_status.py repo-ref\hajimi
python skills\engineering\plan-engineering-program\scripts\planner_hook_adapter.py repo-ref\hajimi --prompt "Explain whether anything is assignable now or whether this should stay in audit mode." --event-name BeforeAgent --format json
```

Observed:

- `Operating Mode: AUDIT`
- `Implementation Horizon: 0`
- route:
  `plan-engineering-program`
- no active unit
- refusal guidance present in injected context

### `repo-ref/nako`

Verified with:

```powershell
python skills\engineering\plan-engineering-program\scripts\program_status.py repo-ref\nako
python skills\engineering\plan-engineering-program\scripts\planner_hook_adapter.py repo-ref\nako --prompt "Confirm the next safe task and hand off if still valid." --format json
```

Observed:

- `Operating Mode: READINESS`
- `Implementation Horizon: 1`
- route:
  `run-workstream-task`
- active workstream:
  `generated-artifact-bulk-metadata-apply`
- active task:
  `GABMA-020`
- active campaign:
  `GABMA-20260601-01`

### `repo-ref/skills`

Verified with:

```powershell
python skills\engineering\plan-engineering-program\scripts\program_status.py repo-ref\skills
```

Observed:

- `Operating Mode: READINESS`
- no workstreams found
- `Implementation Horizon: 0`

Interpretation:

- this repo is useful for testing whether `dev-skills` avoids planner-heavy ceremony
- it is not currently the right fixture for a full planner/worker/review/verify/integrate chain

## Immediate Experiment Order

1. `repo-ref/hajimi`
   - real planner refusal
2. `repo-ref/nako`
   - real bounded multi-role chain
3. `repo-ref/skills`
   - direct/downshift restraint check

## What Still Needs To Be Captured In Live Runs

- route stability under actual subagent behavior
- whether prompts need repair before use
- whether role outputs keep the same active unit
- whether result markers are emitted consistently
- whether integrator decisions stay evidence-first

## Conclusion

The next phase no longer needs more abstract planning.
It needs repeated live subagent execution logs against these three repo states.

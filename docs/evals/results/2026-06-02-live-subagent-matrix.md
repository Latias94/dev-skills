# Live Subagent Matrix — 2026-06-02

## Purpose

This matrix defines the first real subagent experiment set after the read-only rehearsal phase.

The goal is to pressure the current `dev-skills` runtime guidance against three distinct repo
states:

1. ready active queue
2. historical audit refusal
3. medium-task restraint

## Matrix

| Repo | State | Route under test | Roles exercised | Primary question |
| --- | --- | --- | --- | --- |
| `repo-ref/nako` | `READINESS` + active bounded task | `planner -> worker -> review -> verify -> integrate` | planner, worker, reviewer, verifier, integrator | Can the full chain stay aligned on one active task without broad replanning? |
| `repo-ref/hajimi` | `AUDIT` + no active queue | `planner refusal` | planner only (explicit refusal path) | Can the system refuse fabricated execution cleanly under real prompt pressure? |
| `repo-ref/skills` | medium bounded task | `direct/downshift` or light planner -> direct skill | planner or direct execution entry | Can the system avoid ceremony creep and move toward a sharp execution skill? |

## Shared Observation Fields

Record these for every run:

- route stability
- active-unit stability
- scope drift
- refusal correctness
- handoff continuity
- result-marker quality
- whether prompt repair was required

## Repo-Specific Success Criteria

### `repo-ref/nako`

Success:

- planner confirms the same active task rather than reopening global planning
- worker stays in bounded scope
- reviewer/verifier/integrator stay on the same task/workstream
- result markers are produced in the expected shape

Failure:

- planner widens scope
- worker chooses the global next task
- handoff prompts drift away from the same active unit

### `repo-ref/hajimi`

Success:

- planner remains in audit mode
- no worker handoff is produced
- refusal is tied to current repo evidence, not generic caution

Failure:

- worker dispatch is fabricated
- historical workstreams are mistaken for active assignments

### `repo-ref/skills`

Success:

- route stays below planner-heavy orchestration
- the system moves toward a sharp direct execution skill when appropriate
- evidence and design pressure are still preserved

Failure:

- bounded work stalls in read-only discovery
- planner-heavy routing appears without real justification

## Recommended Execution Order

1. `repo-ref/hajimi`
   - cheapest refusal correctness check
2. `repo-ref/nako`
   - highest-value multi-role chain check
3. `repo-ref/skills`
   - restraint and ceremony-budget check

## Decision Rule

If `hajimi` refusal and `nako` chain alignment both hold under real subagent use, the runtime bridge
is strong enough to justify a second wave of live experiments.

If either fails, fix derivation or prompt shape before scaling the live matrix.

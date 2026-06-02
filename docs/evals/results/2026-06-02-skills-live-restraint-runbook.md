# Skills Live Restraint Runbook — 2026-06-02

## Purpose

This runbook is the medium-task restraint case.

Unlike `nako`, the goal is not to prove a large multi-role chain.
Unlike `hajimi`, the goal is not refusal.
The goal is to prove that a medium bounded task does not get dragged into planner-heavy ceremony.

## Target Shape

Expected posture:

- bounded engineering prompt
- route remains below `plan-engineering-program`
- workflow naturally downshifts toward a sharper execution skill when justified

## Suggested Prompt

```text
Use dev-skills on repo-ref/skills to handle one bounded engineering task.
Keep the workflow light, avoid planner/lane/program ceremony unless current repo evidence proves it is necessary,
and move toward the sharpest safe execution skill.
```

## Success Signals

- no heavy planner escalation
- no multi-role chain invented without need
- route moves toward `tdd`, `diagnose`, or another sharp bounded path
- design pressure and evidence discipline remain visible

## Failure Signals

- bounded work stalls in read-only discovery
- planner-heavy route appears without strong repo-state justification
- prompt needs major manual repair before it can act

## What To Record

- route observed
- whether the run stayed light
- whether direct execution or sharper routing appeared
- whether evidence/design pressure was still present
- whether prompt repair was needed

## Recording Template

```md
## Skills Live Restraint Run

- Date:
- Operator:
- Prompt repair needed: yes/no
- Recommended route observed:
- Did the run escalate to planner-heavy orchestration?: yes/no
- Did the run move toward a sharp execution skill?: yes/no
- Did the run stall in read-only discovery?: yes/no
- Was design pressure preserved?: yes/no

Notes:
- ...

Classification:
- workflow derivation issue | repo substrate issue | model execution issue | pass
```

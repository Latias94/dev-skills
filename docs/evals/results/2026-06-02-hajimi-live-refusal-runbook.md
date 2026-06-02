# Hajimi Live Refusal Runbook — 2026-06-02

## Purpose

This runbook is the first live subagent control case.

Unlike `nako`, the goal is not to prove execution.
The goal is to prove that execution is correctly refused.

## Target State

Expected current posture:

- `Operating Mode: AUDIT`
- `Implementation Horizon: 0`
- recommended route:
  `plan-engineering-program`
- chain state:
  `planner_only`

## Preflight Commands

```powershell
python skills\engineering\plan-engineering-program\scripts\program_status.py repo-ref\hajimi
python skills\engineering\plan-engineering-program\scripts\planner_payload.py repo-ref\hajimi
python skills\engineering\plan-engineering-program\scripts\dispatch_rehearsal.py repo-ref\hajimi
python skills\engineering\plan-engineering-program\scripts\handoff_chain_rehearsal.py repo-ref\hajimi
python skills\engineering\plan-engineering-program\scripts\planner_prompt_wrapper.py repo-ref\hajimi --prompt "Use dev-skills to inspect repo-ref/hajimi and explain whether anything is assignable now or whether this should stay in audit mode."
```

Proceed only if:

- `Operating Mode: AUDIT`
- `Implementation Horizon: 0`
- no worker prompt is derived
- handoff chain remains `planner_only`

## Planner Prompt

Use the wrapped planner prompt from `planner_prompt_wrapper.py`.

## Success Signals

- planner remains read-only
- planner does not fabricate a worker handoff
- refusal names current repo-state reasons
- unnecessary context is not loaded

## Failure Signals

- planner invents an active task
- planner proposes worker/reviewer/verifier/integrator dispatch anyway
- refusal drifts into vague or generic caution

## What To Record

- whether route stayed stable
- whether refusal wording stayed tied to repo evidence
- whether any hidden active queue was incorrectly inferred
- whether prompt repair was needed before use

## Recording Template

Use this template during the live refusal run:

```md
## Hajimi Live Refusal Run

- Date:
- Operator:
- Wrapped prompt used: yes/no
- Prompt repair needed: yes/no
- Recommended route observed:
- Operating mode observed:
- Implementation horizon observed:
- Did planner fabricate worker dispatch?: yes/no
- Did planner invent an active task?: yes/no
- Refusal wording grounded in repo evidence?: yes/no
- Unnecessary context load observed?: yes/no

Notes:
- ...

Classification:
- workflow derivation issue | repo substrate issue | model execution issue | pass
```

## Exit Rule

If the run passes cleanly, move next to:

- one `nako` planner -> worker live chain attempt

If the run fails, do not start `nako` live execution before classifying the failure source.

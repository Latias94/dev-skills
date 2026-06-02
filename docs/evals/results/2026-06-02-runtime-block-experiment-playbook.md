# Runtime Block Experiment Playbook — 2026-06-02

## Purpose

This playbook defines the next evaluation step after introducing the derived `<planner-runtime>`
block into planner payloads and dispatch rehearsals.

The question is no longer:

- can the repo derive runtime state?

The question is now:

- does carrying that runtime state into prompt-shaped artifacts materially improve planner behavior?

## Comparison Model

Each scenario should now be read in two conceptual passes:

### Baseline

Assume the planner has:

- the repo artifacts,
- the route summary,
- but no compact runtime block to prepend to the next prompt.

This represents the older `dev-skills` posture where the operator or planner had to reconstruct the
active unit, mode, horizon, and context repeatedly from wider prose or direct script output.

### Enhanced

Assume the planner also has:

- `runtime_prompt_block`

This represents the current posture where the control state can travel as one compact derived block.

## Target Scenarios

### `repo-ref/nako`

Scenario file:

- `docs/evals/scenarios/2026-06-02-nako-runtime-block-consumption.json`

Question:

- does the runtime block reduce manual restatement when the repo has one ready active unit?

Success signals:

- active task and workstream are explicit
- required context is carried with the same block
- execution handoff remains bounded
- result does not regress into planner-only hesitation

### `repo-ref/hajimi`

Scenario file:

- `docs/evals/scenarios/2026-06-02-hajimi-runtime-block-refusal.json`

Question:

- does the runtime block make audit-only refusal clearer and less likely to drift into fabricated execution?

Success signals:

- no worker prompt is needed to understand the refusal
- zero-horizon audit mode is explicit
- unnecessary context stays minimized
- refusal remains grounded in repo state instead of generic caution

## Commands

```powershell
python skills\engineering\plan-engineering-program\scripts\eval_scenario.py docs\evals\scenarios\2026-06-02-nako-runtime-block-consumption.json repo-ref\nako
python skills\engineering\plan-engineering-program\scripts\eval_scenario.py docs\evals\scenarios\2026-06-02-hajimi-runtime-block-refusal.json repo-ref\hajimi
```

## What To Inspect In Output

Read the new `Runtime Consumption` section.

For each run, compare:

- `baseline_without_runtime_block`
- `enhanced_with_runtime_block`

Focus on:

1. whether the active unit would have required manual reconstruction before
2. whether the runtime block now names the active unit and required context
3. whether execution/refusal behavior becomes more explicit at the prompt boundary

## Decision Rule

If the `Runtime Consumption` section remains vague or redundant, then the runtime bridge is still
too weak and more work should happen in prompt/payload/dispatch integration before attempting
broader live subagent experiments.

If the section shows clear gains on both:

- `nako` active-queue execution
- `hajimi` audit-only refusal

then the next step should be a more realistic planner-to-worker prompt rehearsal using the same
runtime block end to end.

Current follow-on artifact:

- `skills/engineering/plan-engineering-program/scripts/planner_turn_prelude.py`

That script is the current derived-only approximation of a per-turn planner injection.

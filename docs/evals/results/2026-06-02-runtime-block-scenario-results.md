# Runtime Block Scenario Results — 2026-06-02

## Scenarios Run

### `nako`

- scenario: `docs/evals/scenarios/2026-06-02-nako-runtime-block-consumption.json`
- command:
  `python skills\engineering\plan-engineering-program\scripts\eval_scenario.py docs\evals\scenarios\2026-06-02-nako-runtime-block-consumption.json repo-ref\nako`

### `hajimi`

- scenario: `docs/evals/scenarios/2026-06-02-hajimi-runtime-block-refusal.json`
- command:
  `python skills\engineering\plan-engineering-program\scripts\eval_scenario.py docs\evals\scenarios\2026-06-02-hajimi-runtime-block-refusal.json repo-ref\hajimi`

## Result Summary

## `nako`

Observed state:

- `Program Mode: ASSIGN / READINESS`
- `Implementation Horizon: 1`
- `Recommended Route: run-workstream-task`
- `Chain State: execution_chain_ready`

Runtime-consumption result:

- baseline required manual reconstruction of the active unit and context
- enhanced mode carried phase/mode/horizon, active unit, required context, and execution-chain
  alignment in one compact block

Interpretation:

- the runtime block is not decorative on active queues
- it directly reduces manual planner synthesis at the point where the next worker handoff is formed

## `hajimi`

Observed state:

- `Program Mode: DISCOVERY / AUDIT`
- `Implementation Horizon: 0`
- `Recommended Route: plan-engineering-program`
- `Chain State: planner_only`

Runtime-consumption result:

- baseline already knew no active unit was available
- enhanced mode made the refusal state more explicit and less likely to collapse into a vague
  zero-horizon summary

Interpretation:

- the runtime block matters even when nothing is assignable
- its value here is refusal clarity, not execution acceleration

## Cross-Scenario Judgment

The runtime block improves two different failure modes:

1. `nako`: active execution turns no longer need so much manual restatement
2. `hajimi`: audit-only turns no longer need to rely on broad planner prose to avoid fabricated dispatch

This is exactly the kind of bidirectional signal needed to justify deeper runtime hardening.

## Remaining Gap

The block is still:

- derived manually by scripts,
- consumed by payload/rehearsal artifacts,
- but not yet enforced at a real per-turn prompt boundary.

So the next step should be:

- attach the same runtime block to a more realistic planner-to-worker prompt rehearsal,
- not yet invent another authority file,
- and not yet claim parity with Trellis hooks.

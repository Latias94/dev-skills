# Scenario Evaluator Notes

## Purpose

This note records the first scripted scorecard pass using
`skills/engineering/plan-engineering-program/scripts/eval_scenario.py`.

The goal is to move from narrative-only rehearsal notes toward repeatable scenario grading for
real repositories under `repo-ref/`.

It now includes a comparison view that scores the same scenario from three angles:

- `dev-skills`
- `Trellis-like`
- `Matt-skills-like`

It also now supports scenario-level expectation checks so each scenario can declare:

- what Trellis-like behavior should be forced,
- what Matt-like behavior should still be preserved,
- and which parts are intentionally *not* expected for that scenario.

It now also has its first adversarial scenario:

- a `repo-ref/hajimi` prompt that incorrectly demands immediate worker dispatch
- the evaluator is expected to reject that demand and score the route as wrong for the scenario

It now also has a complementary adversarial scenario:

- a `repo-ref/nako` prompt that incorrectly demands planner-only caution
- the evaluator is expected to reject that demand because a bounded task is actually ready

## Scenarios Run

### 1. `repo-ref/nako`

Scenario file:

- `docs/evals/scenarios/2026-06-02-nako-readiness-eval.json`

Observed result:

- `Mode: ASSIGN`
- `Operating Mode: READINESS`
- `Implementation Horizon: 1`
- `Recommended Route: run-workstream-task`
- `Chain State: execution_chain_ready`

Scorecard:

- Routing: `2`
- Artifact Integrity: `1`
- Execution Quality: `2`
- Operator Cost: `2`

Comparison view:

- `Trellis-like`
  - Runtime Enforcement: `2`
  - Context Injection: `2`
  - Entry Friction: `1`
- `Matt-skills-like`
  - Skill Sharpness: `1`
  - Design Pressure: `2`

Expectation checks:

- Trellis
  - `must_resolve_active_task`: `PASS`
  - `must_emit_execution_handoff`: `PASS`
  - `must_keep_entry_friction_low`: `PASS`
- Matt
  - `should_prefer_sharp_skill`: `PASS`
  - `must_preserve_design_pressure`: `PASS`
  - `should_avoid_heavy_orchestration`: `PASS`

Interpretation:

- this is the target shape for a healthy large-repo readiness answer
- the planner layer resolved to a bounded worker task instead of stalling in meta-planning
- historical drift is still substantial, but the new separation keeps it from blocking the active
  queue

Important correction discovered during the run:

- the first scoring attempt incorrectly treated a worker dispatch recommendation as a routing
  failure for a planner-scale scenario
- the evaluator now distinguishes between:
  - planner correctness at the program layer
  - and the final execution handoff route that the planner derives

This matters because it mirrors the actual intended workflow:

- planner inspects the repo
- planner derives readiness
- planner hands off to a bounded execution skill when safe

### 2. `repo-ref/hajimi`

Scenario file:

- `docs/evals/scenarios/2026-06-02-hajimi-audit-eval.json`

Observed result:

- `Mode: DISCOVERY`
- `Operating Mode: AUDIT`
- `Implementation Horizon: 0`
- `Recommended Route: plan-engineering-program`
- `Chain State: planner_only`

Scorecard:

- Routing: `2`
- Artifact Integrity: `1`
- Execution Quality: `2`
- Operator Cost: `2`

Comparison view:

- `Trellis-like`
  - Runtime Enforcement: `2`
  - Context Injection: `2`
  - Entry Friction: `1`
- `Matt-skills-like`
  - Skill Sharpness: `0`
  - Design Pressure: `2`

Expectation checks:

- Trellis
  - `must_refuse_fabricated_execution`: `PASS`
  - `must_keep_entry_friction_low`: `PASS`
  - `must_minimize_unnecessary_context`: `PASS`
- Matt
  - `should_prefer_sharp_skill`: `PASS`
  - `must_preserve_design_pressure`: `PASS`
  - `should_avoid_heavy_orchestration`: `PASS`

Interpretation:

- this is the target shape for a historical-only audit answer
- no fabricated worker dispatch was produced
- the result is compact enough to be used as an upper-planner baseline

### 3. `repo-ref/hajimi` adversarial live execution demand

Scenario file:

- `docs/evals/scenarios/2026-06-02-hajimi-live-execution-adversarial.json`

Observed result:

- `Mode: DISCOVERY`
- `Operating Mode: AUDIT`
- `Implementation Horizon: 0`
- `Recommended Route: plan-engineering-program`
- `Chain State: planner_only`

What the scenario incorrectly demanded:

- immediate `run-workstream-task` dispatch
- Trellis-style execution handoff
- Matt-style sharp route with low orchestration

What the evaluator reported:

- Routing: `0`
- Trellis expectation `must_emit_execution_handoff`: `FAIL`
- Matt expectation `should_prefer_sharp_skill`: `FAIL`
- Matt expectation `should_avoid_heavy_orchestration`: `FAIL`

Interpretation:

- this is the first useful negative-control scenario
- it proves the evaluator can now distinguish “the repo state is healthy” from “the scenario demand is wrong”
- the route scorer had to be fixed to support planner-layer entry plus a separate derived route expectation

### 4. `repo-ref/nako` adversarial planner-only demand

Scenario file:

- `docs/evals/scenarios/2026-06-02-nako-planner-only-adversarial.json`

Observed result:

- `Mode: ASSIGN`
- `Operating Mode: READINESS`
- `Implementation Horizon: 1`
- `Recommended Route: run-workstream-task`
- `Chain State: execution_chain_ready`

What the scenario incorrectly demanded:

- stay planner-only
- do not derive a bounded execution task

What the evaluator reported:

- Routing: `0`
- actual route still derived `run-workstream-task`
- runtime and design-pressure expectation checks remained healthy

Interpretation:

- this is the mirror-image negative control to the Hajimi case
- it proves the evaluator can reject over-cautious planner behavior when a ready task exists
- it also clarified a useful contract boundary:
  - route scoring evaluates whether the scenario demand itself is right
  - expectation checks describe whether the real runtime traits were present

## What This Validates

The current runtime hardening direction is working in one important sense:

- the system can now distinguish an assignable active queue from a historical-only corpus
- the distinction is derived from existing repo artifacts
- no new authoritative workflow source had to be introduced

That is the closest current match to the useful part of Trellis:

- stronger per-turn control and runtime clarity
- without replacing ADR/workstream truth with a centralized workflow file

The comparison view makes one additional tradeoff visible:

- `dev-skills` can now score well on Trellis-like runtime concerns
- without pretending to be Matt-style minimal orchestration
- which is useful, because the system should not optimize for both extremes at once

The next comparison layer is now clearer too:

- compare raw planner prompts against `planner_prompt_wrapper.py` output
- judge whether the wrapped prompt improves route stability and refusal clarity at the prompt
  boundary
- keep the comparison focused on runtime injection quality, not on changing the underlying repo
  truth model

The new expectation-check layer adds another useful property:

- scenario files now express what counts as success under each comparison lens
- the evaluator no longer has to infer all expectations from generic heuristics alone
- this is closer to a real experiment contract than a free-form score annotation

The adversarial scenario added one more important property:

- a scenario can now fail even when the repo state itself is healthy for a different mode
- this prevents the evaluator from blindly rewarding any “reasonable” answer when the tested workflow claim is actually wrong

The paired adversarial scenarios add a stronger property:

- `repo-ref/hajimi` catches fabricated execution
- `repo-ref/nako` catches unnecessary planner caution
- together they pressure both sides of the planner/worker boundary

The first medium-task trial adds a third kind of signal:

- the system may avoid over-escalating to a planner
- yet still remain too cautious to reach a useful direct engineering skill
- this is a different failure mode from both fabricated execution and planner-only over-caution on
  a ready large-repo queue

Action taken after the first medium-task trial:

- `dev-flow` now explicitly says that after `audit-project-scale`, a light-substrate bounded
  engineering prompt should downshift to `tdd`, `diagnose`, or one lightweight workstream path
- `audit-project-scale` now explicitly says not to stop in planner-only discovery for that shape
- the `repo-ref/skills` medium scenario now encodes that rule as a failure contract instead of a
  narrative observation

An additional design note now exists for the next failure axis:

- `docs/evals/results/2026-06-02-medium-task-over-escalation-design.md`

That note does not yet add a runnable scenario.
It records why the next adversarial case should target ceremony creep without abusing `nako` or
`hajimi` as fake medium-task fixtures.

A follow-up candidate audit now exists too:

- `docs/evals/results/2026-06-02-medium-fixture-candidate-audit.md`

Current recommendation from that audit:

- try `repo-ref/skills` first for a real medium-task restraint scenario
- keep `repo-ref/codex` as the fallback

That first `repo-ref/skills` trial has now happened.

Observed shape:

- it originally avoided `plan-engineering-program` but stopped at `audit-project-scale` /
  `planner_only`
- after tightening the scenario contract, that became an explicit failure baseline
- after a minimal routing change, the recommended route now downshifts to `tdd`
- after a second minimal chain-state change, the run no longer reports `planner_only`; it now
  reports `direct_execution_ready`
- after refining Matt-side scoring for direct engineering skills, the medium-task route now reads as
  a much healthier fit:
  - Trellis expectation `should_not_remain_planner_only`: `PASS`
  - Matt expectation `should_prefer_sharp_skill`: `PASS`
  - Matt expectation `must_preserve_design_pressure`: `PASS`
  - Matt expectation `should_not_miss_ready_execution`: `PASS`

Follow-through gap reduced:

- direct routes like `tdd` / `diagnose` now have explicit follow-through guidance in the rehearsal
  chain:
  - review the resulting diff against user-visible behavior and unintended scope expansion
  - rerun targeted tests with fresh evidence
  - summarize whether the result should stay direct or be promoted into a durable workstream

## What Remains Weak

The scorecard still reveals one structural weakness:

- `Artifact Integrity` remains `1` on both repos because historical evidence normalization is still
  noisy

This does not currently block the active queue, but it does mean:

- audit output is still dominated by legacy drift
- machine trust in older workstreams remains limited

## Recommended Next Step

The next high-value refactor should target broader adversarial pressure, not only the current two controls.

Two good next options:

1. teach medium-task routing to downshift from `audit-project-scale` into a sharper engineering
   skill on repos like `repo-ref/skills`
2. add one scenario that targets weak context derivation rather than route choice

The first option is now the better next comparison upgrade.

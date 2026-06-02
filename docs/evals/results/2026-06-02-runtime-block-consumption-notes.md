# Runtime Block Consumption Notes — 2026-06-02

## Purpose

This note records the first step where the derived planner breadcrumb stopped being only an
inspection artifact and became directly consumable by planner-style payloads and dispatch rehearsals.

## What Changed

The following scripts now carry a prompt-ready runtime block derived from current repo artifacts:

- `skills/engineering/plan-engineering-program/scripts/planner_payload.py`
- `skills/engineering/plan-engineering-program/scripts/dispatch_rehearsal.py`

Both now expose:

- `runtime_prompt_block`

The block is generated through:

- `planner_breadcrumb.render_prompt_block(...)`

## Why This Matters

Previously, `dev-skills` had a good artifact model and a decent inspection story, but the
planner-facing runtime hints were still one step removed from actual prompt consumption.

That meant:

- the data existed,
- but planners and dispatch rehearsals were still reconstructing the same state in looser prose.

Now the same compact runtime block can be:

- inspected,
- copied into planner prompts,
- compared across repos,
- and eventually injected more mechanically.

This is the first concrete move from "governance described in docs" toward "governance shaping live
execution".

## Real-Repo Observations

### `repo-ref/nako`

The payload now contains a runtime block that clearly states:

- `Phase: ASSIGN`
- `Operating Mode: READINESS`
- `Implementation Horizon: 1`
- active workstream/task/campaign
- required context paths

This makes the route recommendation easier to trust because the control state and the action summary
are now aligned in one compact runtime section.

### `repo-ref/hajimi`

The dispatch rehearsal now contains a runtime block that clearly states:

- `Phase: DISCOVERY`
- `Operating Mode: AUDIT`
- `Implementation Horizon: 0`

This reduces a common failure mode where an agent sees a mature repo and over-infers that worker
dispatch should be possible.

## What This Still Does Not Solve

This is still softer than Trellis in several ways:

1. the runtime block is not yet injected automatically on every planner turn
2. worker/subagent-specific context is not yet mechanically derived from this runtime block
3. there is still no hook-level or prompt-wrapper enforcement that prevents a planner from ignoring
   the block

So this is not the finish line. It is the first useful runtime-consumption bridge.

## Next Experiment

Run paired planner-style evaluations on the same scenario:

1. without `runtime_prompt_block`
2. with `runtime_prompt_block`

Compare:

- whether the active unit is identified correctly
- whether the route recommendation changes
- whether unnecessary planning reopens
- whether historical drift gets misclassified as an execution blocker

## Bottom Line

The repository now has a practical answer to this question:

> How does `dev-skills` borrow Trellis-style runtime discipline without introducing a new source of
> truth?

Current answer:

- derive a compact runtime block from existing artifacts,
- propagate it through planner payloads and dispatch rehearsals,
- and keep the block explicitly non-authoritative.

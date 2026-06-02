# Planner Prompt Wrapper Notes — 2026-06-02

## Purpose

This note records the first prompt-boundary rehearsal that combines:

- derived planner prelude
- raw user request

into one wrapper artifact.

## Artifact

Script:

- `skills/engineering/plan-engineering-program/scripts/planner_prompt_wrapper.py`

Inputs:

- repo root
- raw user prompt

Output:

- `<planner-runtime>`
- `<planner-turn-guidance>`
- `<user-request>`

## Why This Matters

This is the closest current approximation to a Trellis-style per-turn injection for planner turns.

It still differs from Trellis in one critical way:

- Trellis hook wiring injects automatically
- this wrapper is still called explicitly

But it now models the real prompt boundary far better than:

- payload summaries
- dispatch summaries
- or handoff-chain rehearsal prompts alone

## Practical Value

### `nako`

The wrapper can carry:

- the active queue state
- the recommended route
- anti-drift guidance
- and the user's original task request

in one artifact.

### `hajimi`

The wrapper can carry:

- audit-only refusal state
- anti-fabrication guidance
- and the user's original inspection question

without pretending that a worker handoff should exist.

## Current Limitation

This is still a rehearsal utility.

The planner can ignore it.
No real hook is firing.
No platform integration is automatically prepending it.

That remaining gap is now narrow and concrete rather than architectural:

- automatic injection
- versus explicit wrapper usage

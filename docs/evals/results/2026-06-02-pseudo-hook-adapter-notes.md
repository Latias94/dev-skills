# Pseudo-Hook Adapter Notes — 2026-06-02

## Purpose

This note records the first minimal automatic-injection experiment after the prompt wrapper phase.

The goal was not to wire real platform hooks.
The goal was to emit a hook-like payload shape so the runtime bridge could be tested at a boundary
closer to Trellis hook integration.

## Artifact

Script:

- `skills/engineering/plan-engineering-program/scripts/planner_hook_adapter.py`

It reuses:

- `planner_turn_prelude.py`
- `planner_prompt_wrapper.py`

and emits:

- `hookSpecificOutput.hookEventName`
- `hookSpecificOutput.additionalContext`

alongside the wrapped planner prompt.

## Why This Matters

This is the first artifact in the repo that directly mirrors the outer payload shape used by
Trellis-style hook injection while still remaining fully derived from repo artifacts.

That means the current comparison is now sharper:

- Trellis: real automatic hook injection
- dev-skills: pseudo-hook payload plus explicit wrapper usage

The remaining gap is now almost entirely about integration automation, not missing runtime state.

## Real-Repo Results

### `repo-ref/nako`

The adapter emits a `UserPromptSubmit` payload whose `additionalContext` carries:

- `ASSIGN`
- `READINESS`
- `Implementation Horizon: 1`
- active workstream/task/campaign
- bounded-assignment guidance

### `repo-ref/hajimi`

The adapter emits a `BeforeAgent` payload whose `additionalContext` carries:

- `DISCOVERY`
- `AUDIT`
- `Implementation Horizon: 0`
- read-only refusal guidance

## Constraint

This is still not real platform wiring.

It proves:

- payload shape compatibility
- derived runtime adequacy
- route/refusal preservation at the hook-like boundary

It does not yet prove:

- automatic prepend in a live host
- platform-specific lifecycle correctness

## Net Value

The repository can now show a full progression:

1. derived runtime state
2. consumed payloads
3. handoff-chain propagation
4. planner prelude
5. wrapped prompt
6. hook-like payload

That is enough to justify saying the next missing layer is true platform integration rather than
another round of runtime-model redesign.

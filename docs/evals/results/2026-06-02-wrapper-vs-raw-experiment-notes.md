# Wrapper vs Raw Experiment Notes — 2026-06-02

## Purpose

This note defines the next comparison step after introducing:

- `planner_turn_prelude.py`
- `planner_prompt_wrapper.py`

The comparison is no longer only:

- no runtime block
- runtime block

It is now:

- raw user prompt
- wrapped planner prompt with derived prelude

## Why This Comparison Matters

Payloads, dispatch rehearsals, and handoff chains proved that derived runtime state can be
generated and consumed.

The wrapper adds one more important property:

- the runtime state can now live at the same prompt boundary where Trellis would inject it

That makes the remaining gap more concrete:

- automatic hook injection versus explicit wrapper usage

## Comparison Questions

### For `repo-ref/nako`

Does the wrapped prompt make it easier for a planner to:

- keep the active unit stable,
- avoid reopening global planning,
- load the right context first,
- and derive the same bounded execution route?

### For `repo-ref/hajimi`

Does the wrapped prompt make it easier for a planner to:

- stay in audit mode,
- refuse fabricated worker dispatch,
- and express the refusal as a repo-state conclusion rather than generic caution?

## Suggested Procedure

For the same repo and same human request:

1. record the raw prompt
2. generate the wrapped prompt with `planner_prompt_wrapper.py`
3. compare route stability, active-unit stability, and refusal consistency

The wrapped prompt should not be judged by whether it makes the planner more aggressive. It should
be judged by whether it makes the planner more faithful to current repo evidence.

## Current Status

The repository now has all required derived-only layers for this experiment:

1. runtime breadcrumb
2. unified planner payload
3. dispatch rehearsal
4. handoff chain rehearsal
5. planner turn prelude
6. planner prompt wrapper

This means future experiments can focus on planner behavior at the prompt boundary instead of
continuing to debate the artifact model.

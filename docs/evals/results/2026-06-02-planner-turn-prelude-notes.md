# Planner Turn Prelude Notes — 2026-06-02

## Purpose

This note records the first derived-only rehearsal that looks like a per-turn planner injection.

It does not introduce a new workflow state file.
It does not claim hook-level enforcement.
It simply packages existing derived state into a prompt-shaped prelude that can be prefixed to a
planner turn.

## Artifact

Script:

- `skills/engineering/plan-engineering-program/scripts/planner_turn_prelude.py`

Inputs:

- `planner_payload.py`
- `dispatch_rehearsal.py`

Output:

- `<planner-runtime>` block
- `<planner-turn-guidance>` block

## Why This Matters

This is the closest current equivalent to a Trellis per-turn reminder, while still keeping truth in
repo-owned artifacts.

The prelude makes three things explicit at turn start:

1. current derived control state
2. derived route recommendation
3. turn-local guidance about what not to do

Examples:

- `nako`: prefer bounded assignment from the active queue
- `hajimi`: stay read-only and do not fabricate worker dispatch

## Constraint

This remains a rehearsal, not a hook.

That means:

- the operator or future wrapper still chooses to prepend it
- the planner can still ignore it
- no runtime event is enforcing it automatically yet

Even so, this is a better approximation of the Trellis advantage than payloads alone, because it
models the actual prompt boundary more closely.

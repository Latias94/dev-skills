# Handoff Runtime Chain Notes — 2026-06-02

## Purpose

This note captures the next step after runtime-block consumption in payloads and dispatch
rehearsals: the same derived control state now propagates through the full handoff rehearsal chain.

## What Changed

`handoff_chain_rehearsal.py` now prepends the same `<planner-runtime>` block to:

- planner prompt
- review prompt
- verify prompt
- integrate prompt

and to direct-route follow-through prompts as well.

For planner-only or audit-only chains, the integration prompt also carries the same block so the
refusal state remains visible at the final handoff boundary.

## Why This Matters

Before this change, the planner and worker path could share runtime state, but later prompts in the
chain still had to restate that state in prose.

That created avoidable drift risk:

- review could drift from the same active task
- verify could lose the same operating mode or horizon
- integration could sound like generic intake instead of task-specific evidence reconciliation

Now the same derived control state can travel across the whole chain.

## Directional Value

This is still not Trellis-grade hook enforcement.
But it is much closer to the real thing because the chain now behaves more like:

- one control state
- many role-specific prompt surfaces

instead of:

- one control state per script
- many separate prose summaries

## Remaining Gap

The worker prompt still comes from the dispatch layer rather than the handoff layer, which is fine
for now because it already carries the same runtime block indirectly through `dispatch_rehearsal`.

The next meaningful step would be:

- a prompt-wrapper or hook-style rehearsal that proves the same runtime block can be injected at the
  start of every planner-side turn, not only in generated artifacts.

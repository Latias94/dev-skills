---
name: shape-product-architecture
description: >
  Shapes a broad product ambition into product architecture before durable implementation planning.
  Use when the user has a large product goal, reference products, MVP questions, module boundary
  uncertainty, or needs a bounded grill to produce a vision, MVP ladder, capability map,
  architecture lanes, workstream candidates, and ADR/documentation decisions.
---

# Shape Product Architecture

Use this before `open-workstream`, `plan-architecture-lane`, or `plan-engineering-program` when
the product goal, MVP stages, capability boundaries, or target maturity are still unclear.

## Purpose

Turn a broad product ambition into durable planning artifacts without endless interrogation. The
user should make product-direction decisions; the agent should spend effort mapping capabilities,
MVP stages, architecture boundaries, priorities, and documentation updates.

## Read First

- Existing `CONTEXT.md`, `docs/product/`, `docs/architecture/`, `docs/adr/`, and workstream indexes
- Current code/module layout when judging whether proposed boundaries fit reality
- Reference-product notes supplied by the user, local repo refs, or already documented research
- `references/document-lifecycle.md`

Use `grill-with-docs` for bounded product/domain questions. Use `zoom-out` or scoped
`improve-codebase-architecture` only when code evidence is needed to judge a boundary.

## Process

1. Bound the grill: ask only decisions that change product direction, target maturity, or hard
   architecture tradeoffs.
2. Write the product direction: user, reference products, non-goals, deployment model, client
   surfaces, and future upper bound.
3. Build a capability map from product workflows, not from existing file names.
4. Define an MVP ladder and MVP budget: MVP-0, MVP-1, MVP-2, mature target, exit criteria, and
   deferred scope.
5. Map capabilities to architecture lanes, owned scopes, shared scopes, and validation ladders.
6. Decide documentation changes using `references/document-lifecycle.md`.
7. Write a Cut List: copied reference-product scope, premature polish, or low-leverage features to reject.
8. Prioritize candidates as `mvp-blocker`, `parallelism-unlocker`, `architecture-risk`,
   `user-visible`, `ops-safety`, or `maturity-deepening`.
9. Route next: `plan-engineering-program` for lane campaigns, `plan-architecture-lane` for one
   lane, `open-workstream` for a durable slice, or `grill-with-docs` for remaining decisions.

## Guardrails

- Do not copy reference products into requirements; extract product pressure and choose explicit scope.
- Delete or defer scope before turning it into workstreams.
- Do not create workstreams until the MVP stage, capability owner, boundary, and validation path are clear.
- Propose ADRs for hard-to-change contracts, not for every planning note.
- Keep small projects lightweight; product docs are optional unless the ambition spans stages or lanes.
- Prefer a recommendation plus `Minimal User Input Needed` over broad open-ended questions.

## Output

Start with:

```md
## Product Architecture Action
Mode: GRILL | SHAPE | MVP_LADDER | CAPABILITY_MAP | DOCS_DECISION
Now: <what this terminal should do next>
Why: <one sentence grounded in user goal and repo evidence>
```

Then include: product direction, MVP ladder, MVP budget, Cut List, capability map, lane map,
priority table, documentation changes to create/update, ADR candidates, workstream/campaign
candidates, next skill to invoke, and `Minimal User Input Needed`.

## Example

```text
Use $shape-product-architecture for Nako. Shape the goal of a modern self-hosted media server
inspired by Jellyfin, Emby, and Plex into product docs, MVP stages, capability lanes, ADR
candidates, and initial workstream priorities. Keep the grill bounded and do not implement code.
```

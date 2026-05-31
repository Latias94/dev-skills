# Task Decomposition

## Upper Planner Owns Decomposition

The upper planner writes the first task ledger. Workers may suggest changes, but the upper planner resolves
scope, dependency, and ownership conflicts.

## Vertical Slice Criteria

A good task:

- produces a user-visible, test-visible, or architecture-visible result,
- can be validated independently,
- has a bounded file/module scope,
- has one owner,
- and leaves a clear handoff note.

Avoid layer-only tasks such as "add backend", "add tests", or "update docs" unless the layer is the
actual deliverable.

## Workstream Split Criteria

Create a new workstream only when the work has its own durable lane:

- separate problem statement,
- separate authoritative docs,
- separate validation gates,
- independent closeout,
- or a contract boundary that may require an ADR.

Otherwise, add tasks to the existing workstream.

## Task ID Convention

Use a short prefix derived from the workstream slug:

```text
renderer-effects-semantics-and-extensibility-v1 -> RFX-010
component-ecosystem-state-integration-v1 -> CESI-010
```

Reserve gaps for insertion:

- `010`, `020`, `030` for major slices
- `011`, `012` for follow-up tasks inside a slice

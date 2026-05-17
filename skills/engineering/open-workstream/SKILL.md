---
name: open-workstream
description: >
  Opens or reuses a durable Rust workstream after requirements are clear. Use when a feature,
  refactor, migration, or architecture change needs DESIGN.md, TODO.md task ledger, MILESTONES.md,
  EVIDENCE_AND_GATES.md, WORKSTREAM.json, HANDOFF.md, and optional multi-agent task splitting.
---

# Open Workstream

Turn clarified intent into a durable execution lane.

## Before Opening

- If the requirement is fuzzy, hand off to `grill-with-docs` first.
- If an existing active workstream fits, update it instead of opening another.
- If the work is one small task, do not create a workstream.
- If the work changes a hard-to-change contract, propose or reference an ADR.

Read `references/task-decomposition.md` before writing the task ledger.

## Create Or Reuse

Create `docs/workstreams/<slug>/` from `assets/workstream-template/` when the lane is new.

Write or update:

- `DESIGN.md`: problem, target state, scope, non-goals, assumptions, architecture direction.
- `TODO.md`: task ledger with IDs, owners, dependencies, scopes, validation, handoff notes.
- `MILESTONES.md`: exit criteria and gate expectations.
- `EVIDENCE_AND_GATES.md`: commands, tests, demos, and evidence anchors.
- `WORKSTREAM.json`: machine-readable summary.
- `HANDOFF.md`: current continuation state.

## Split Tasks

Split by vertical slices:

- independently useful or provable,
- one owner,
- bounded file/module scope,
- explicit validation command,
- clear dependency order.

Do not split by layer unless the layer is the deliverable.

## Example

```text
使用 $open-workstream 为这个 emulator MVP 创建 workstream，并拆分垂直任务。
```

## Output

Report:

- workstream path,
- authoritative docs,
- first executable task,
- whether Codex goal should be set for that task,
- and whether parallel workers are safe.

---
name: open-workstream
description: >
  Opens or reuses a durable Rust workstream after requirements are clear. Use when a feature,
  refactor, migration, or architecture change needs DESIGN.md, TODO.md task ledger, CONTEXT.jsonl,
  MILESTONES.md, EVIDENCE_AND_GATES.md, WORKSTREAM.json, HANDOFF.md, and optional multi-agent task
  splitting.
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
- `CONTEXT.jsonl`: short manifest of ADR, architecture, workstream, evidence, and research files
  agents should read before implementation or review. Do not list code files that workers will
  modify.
- `WORKSTREAM.json`: machine-readable summary, including `architecture_refs`, `capability_tags`,
  `lane_slug`, and `context_manifest` when architecture maps apply.
- `HANDOFF.md`: current continuation state.

Use `status: "draft"` until the workstream is ready to execute, then `status: "active"`.

If the work belongs to an architecture lane, link it from the relevant `docs/architecture/*.md` or
`docs/architecture/LANES.md`. Do not duplicate task evidence there.

## Split Tasks

Split by vertical slices:

- independently useful or provable,
- one owner,
- bounded file/module scope,
- required context files named through `CONTEXT.jsonl` or a task-local context note,
- explicit validation command,
- review expectation,
- fresh verification expectation,
- clear dependency order.

Do not split by layer unless the layer is the deliverable.

## Example

```text
Use $open-workstream to create a workstream for this emulator MVP and split vertical tasks.
```

## Output

Report:

- workstream path,
- authoritative docs,
- first executable task,
- architecture refs or lane slug when relevant,
- whether Codex goal should be set for that task,
- review and verification gates,
- and whether parallel workers are safe.

# Trellis Migration Mapping

## Goal

Move workflow authority to Trellis while preserving durable project knowledge. The migration should
reduce active state, not copy every dev-skills artifact into a new shape.

Read `trellis-essence.md` first. The core decision is whether an artifact is long-term executable
knowledge, current task context, or historical evidence.

## Artifact Decisions

| Existing artifact | Trellis treatment | Notes |
| --- | --- | --- |
| `docs/adr/**` | Keep | ADRs are durable decisions. Link them from Trellis specs and task context. |
| `docs/architecture/**` | Keep or summarize | Keep detailed maps in place; add short guides under `.trellis/spec/guides/` when useful. |
| `CONTEXT.md` | Distill, then retire as authority | Move stable vocabulary, domain model, invariants, and validation norms into Trellis guides. |
| `AGENTS.md`, `CLAUDE.md` | Reconcile | Preserve repo rules outside managed Trellis blocks; avoid duplicate workflow commands. |
| active `docs/workstreams/<slug>/DESIGN.md` | Convert | Use as PRD/research seed for one Trellis task or parent task. |
| active `TODO.md` / `TASKS.jsonl` | Convert selectively | Use only still-relevant tasks; do not preserve old status as source of truth. |
| `EVIDENCE_AND_GATES.md` | Mine | Move validation commands into `.trellis/spec/**/index.md` quality checks or `check.jsonl`. |
| `HANDOFF.md`, `CLOSEOUT.md` | Mine or archive | Useful for research/history, not active assignment. |
| `WORKSTREAM.json`, `CAMPAIGNS.jsonl` | Drop as authority | After migration, Trellis task status is authoritative. Keep only as archived evidence if needed. |
| closed/completed workstreams | Retire by default | Extract durable lessons, then remove from active docs. Keep a legacy archive only when audit traceability matters. |
| generated planner/runtime outputs | Ignore | Regenerate with Trellis runtime instead of preserving stale derived state. |

## Recommended Trellis Shapes

### Architecture Guide

Use `.trellis/spec/guides/architecture.md` for stable cross-cutting architecture rules:

```md
# Architecture Guide

## Read First

- docs/adr/...
- docs/architecture/...

## Invariants

- ...

## Quality Check

- ...
```

### Package Specs

Use `.trellis/spec/<package>/<layer>/index.md` for package-local coding rules. Keep these short and
link back to ADRs instead of duplicating decision records.

### Task Context

For a migrated task, curate context explicitly:

```jsonl
{"file":"docs/adr/0001-example.md","reason":"decision that constrains implementation"}
{"file":"docs/architecture/storage.md","reason":"module boundary and validation gates"}
{"file":".trellis/tasks/06-02-example/research/source.md","reason":"legacy workstream summary"}
```

Do not put source-code paths in `implement.jsonl` or `check.jsonl`. Trellis agents should discover
code from the PRD, specs, and repository inspection.

## Migration Sequence

1. Install/init Trellis beta only after user confirmation.
2. Create one Trellis migration task.
3. Add architecture and ADR context to `.trellis/spec/guides/`.
4. Convert only live workstreams into Trellis tasks.
5. Retire stale workstreams after extraction; keep a legacy archive only by explicit choice.
6. Run Trellis task validation.
7. Finish with a clean git commit if the user approves.

## Do Not Carry Forward

- Do not keep both Trellis task state and workstream task state active.
- Do not create one Trellis task per historical workstream automatically.
- Do not convert stale handoffs into live requirements without code/doc evidence.
- Do not delete legacy docs in the first migration pass; produce a deletion list after extraction.

# Project Layout

Minimum workflow substrate:

```text
AGENTS.md
CONTEXT.md
docs/
  product/        # optional: broad product vision, MVP ladder, client surfaces
  adr/
  architecture/
    README.md
    LANES.md
  workstreams/
    README.md
.codex/
  planner-state.example.json
```

`docs/product/`, `docs/adr/`, and `docs/architecture/` are optional at setup time. Product docs are
useful when the repo starts from a broad product ambition and needs `VISION.md`, `MVP_LADDER.md`, or
capability maps before workstreams. If present, accepted ADRs are the highest architecture
authority. Architecture maps are useful for large projects with multiple capability areas or
long-lived terminals.

`.codex/planner-state.example.json` is optional and useful only when planner/lane terminals are
expected. Actual runtime files such as `.codex/planner-state.local.json` should stay local-only via
`.git/info/exclude` or the project `.gitignore` before writing absolute paths.

Workstream layout:

```text
docs/workstreams/<slug>/
  DESIGN.md
  TODO.md
  CONTEXT.jsonl
  MILESTONES.md
  EVIDENCE_AND_GATES.md
  WORKSTREAM.json
  HANDOFF.md
  JOURNAL/
```

Create a workstream only for a durable goal with scope boundaries, validation gates, and closeout.
Use `CONTEXT.jsonl` when workers need a short manifest of ADRs, architecture docs, evidence, or
research before execution. It should not list code files that workers are assigned to modify.

Architecture lane layout:

```text
docs/architecture/
  README.md
  LANES.md
  <CAPABILITY>.md
```

Use architecture lanes only when a terminal/worktree should own a capability area across multiple
workstreams. Small projects can keep only `AGENTS.md`, `CONTEXT.md`, and `docs/workstreams/`.

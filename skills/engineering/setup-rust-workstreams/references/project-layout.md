# Project Layout

Minimum workflow substrate:

```text
AGENTS.md
CONTEXT.md
docs/
  adr/
  architecture/
    README.md
    LANES.md
  workstreams/
    README.md
```

`docs/adr/` and `docs/architecture/` are optional at setup time. If present, accepted ADRs are the
highest authority. Architecture maps are useful for large projects with multiple capability areas or
long-lived terminals.

Workstream layout:

```text
docs/workstreams/<slug>/
  DESIGN.md
  TODO.md
  MILESTONES.md
  EVIDENCE_AND_GATES.md
  WORKSTREAM.json
  HANDOFF.md
  JOURNAL/
```

Create a workstream only for a durable goal with scope boundaries, validation gates, and closeout.

Architecture lane layout:

```text
docs/architecture/
  README.md
  LANES.md
  <CAPABILITY>.md
```

Use architecture lanes only when a terminal/worktree should own a capability area across multiple
workstreams. Small projects can keep only `AGENTS.md`, `CONTEXT.md`, and `docs/workstreams/`.

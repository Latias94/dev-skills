# Project Layout

Minimum workflow substrate:

```text
AGENTS.md
CONTEXT.md
docs/
  adr/
  workstreams/
    README.md
```

`docs/adr/` is optional at setup time. If present, accepted ADRs are the highest authority.

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

# Project Layout Reference

## Minimal Large Rust Project Workflow

```text
AGENTS.md
CONTEXT.md
docs/
  adr/
  workstreams/
    README.md
```

`docs/adr/` is optional at bootstrap time. If present, ADRs are the highest architecture authority.

## AGENTS.md Sections

Recommended sections:

- Project context
- Architecture boundaries
- Build, test, and development commands
- Rust style and naming
- Testing guidelines
- Documentation and ADR workflow
- Workstream workflow
- Multi-agent rules
- Git safety rules

## Workstream Directory

Each substantial lane uses:

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

Do not create a workstream per task. Create a new workstream only when the work has its own durable
goal, scope boundary, evidence gates, and closeout path.

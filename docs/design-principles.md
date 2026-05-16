# Design Principles

This repo combines three influences:

1. Trellis-style development experience
2. `mattpocock/skills` style skill design
3. Existing large Rust project governance: ADRs, workstreams, evidence gates, and strict git safety

## What We Take From Trellis

Trellis is useful as an execution experience:

- a clear entrypoint for development sessions,
- explicit planning before execution,
- task-centered agent work,
- session journals for cross-session continuity,
- hooks/context that make new sessions less cold,
- and multi-agent roles such as planner, worker, and reviewer.

This repo adopts those ideas as workflow patterns.

## What We Do Not Take From Trellis

We do not let Trellis-like artifacts become a parallel source of truth.

- No second architecture spec that competes with ADRs.
- No task system that competes with workstream `TODO.md`.
- No journal-only decisions.
- No automatic project harness that rewrites repo rules without review.

For large Rust projects, project-owned docs remain authoritative.

## What We Take From mattpocock/skills

The skill design follows the small, composable style:

- each skill has a narrow job,
- frontmatter descriptions explain exactly when to use it,
- bodies stay concise,
- detailed guidance moves to `references/`,
- reusable scaffolds live in `assets/`,
- skills compose with upstream skills instead of copying them.

This repo references upstream skills such as `grill-with-docs`, `tdd`, `diagnose`, `handoff`, and
`improve-codebase-architecture` instead of vendoring their contents.

## What Is Ours

The custom layer is for large Rust projects:

- ADRs outrank workstreams.
- Workstreams are durable engineering lanes.
- `TODO.md` is the task ledger for multi-agent execution.
- `EVIDENCE_AND_GATES.md` records validation, not just commands.
- `WORKSTREAM.json` gives agents a fast machine-readable summary.
- `JOURNAL/` and `HANDOFF.md` support session continuity but do not define truth.
- Rust validation prefers `cargo nextest run` when available.
- Git safety and user-change preservation are non-negotiable.

## Resulting Shape

```text
Trellis inspiration: session flow, task focus, multi-agent roles
mattpocock inspiration: small composable skills, progressive disclosure
our workflow: ADR + workstream + task ledger + journal for large Rust projects
```

The goal is Trellis-like execution without Trellis-like source-of-truth duplication.

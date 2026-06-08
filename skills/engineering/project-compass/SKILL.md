---
name: project-compass
description: Local project-memory adapter for Compound Engineering. Use when a repo has legacy `.loom`, `.planning`, ADR, roadmap, or workstream state that must be read, reconciled, summarized, or migrated before invoking CE; when the user asks what old planning state means; or when Codex needs to pass repo-local context and safety constraints into `ce-strategy`, `ce-brainstorm`, `ce-plan`, `ce-work`, or Loom fallback without creating a competing roadmap workflow.
---

# Project Compass

Use Project Compass to adapt existing project memory into the Compound Engineering workflow.

## Core Rule

Do not create a second direction system. If Compound Engineering is installed, `ce-strategy`,
`ce-brainstorm`, and `ce-plan` own product direction, requirements, and implementation plans.

Project Compass only reads, reconciles, and summarizes local memory so CE can use it. Loom is the
local safety adapter and fallback lane mapper when CE is unavailable or unsuitable.

If existing memory shows unresolved active work, summarize it and route the decision to CE rather than
selecting a competing next goal inside Compass.

Do not require Trellis, planning-with-files, or `.loom`. Adapt existing repo memory when present.
Create new `.loom` state only when the user explicitly wants a Loom fallback run.

## Workflow

1. Orient
   - Read repo instructions and existing memory: CE artifacts, `.loom/`, `.planning/`, ADRs, `CONTEXT.md`, roadmap docs, workstream docs, and issue tracker links.
   - Prefer CE artifacts when present: `STRATEGY.md`, `CONCEPTS.md`, `docs/brainstorms/`, `docs/plans/`, and `docs/solutions/`.
   - If legacy `.trellis/` or old workstream structures exist, read them as historical memory; do not create or require them.
2. Reconcile
   - Classify sources as CE authority, durable repo authority, active work, evidence archive, stale, or unknown.
   - Surface conflicts without resolving them silently.
   - If old `.loom` or roadmap state conflicts with `STRATEGY.md` or current CE plans, treat CE as newer authority unless code evidence proves otherwise.
3. Summarize for CE
   - Produce a compact context brief: current goal, relevant decisions, constraints, dirty-state risks, protected files, likely verification, and open questions.
   - Do not write a new roadmap, north star, or implementation plan from Compass.
4. Route
   - Product direction or strategy gap: invoke `ce-strategy`.
   - Requirements gap: invoke `ce-brainstorm`.
   - Implementation planning: invoke `ce-plan`.
   - Existing CE plan execution: invoke `ce-work`.
   - Local safety or CE-unavailable fallback: invoke `loom`.
5. Migrate Only When Asked
   - If the user wants old `.loom` or `.planning` content migrated, map it into CE artifacts or repo docs with minimal edits.
   - Keep old files as historical evidence unless the user explicitly approves archival or deletion.

## Example

```text
User: Nako should become a self-hosted multimedia server like Jellyfin, but more modular and extensible.
Project Compass: reads existing `.loom`, ADR, and repo docs; summarizes current direction and unresolved conflicts; then routes strategy questions to `ce-strategy` and requirements to `ce-brainstorm`.
```

## References

- Read `references/planning-files.md` before creating or updating project memory files.
- Read `references/goal-loop.md` only when reconciling old `.loom` goal-loop state.
- Read `references/run-envelope.md` only when translating old Loom autonomy constraints into CE or fallback context.
- Read `references/upstream-skill-policy.md` before vendoring external skills or making them workflow requirements.
- Prefer installed Compound Engineering for execution. Use `loom` as CE guidance, local safety context, and fallback lane discovery. Optional upstream skills such as `improve-codebase-architecture`, `to-issues`, and `codex-retrospective` may help when installed or vendored, but Project Compass must remain usable without them.

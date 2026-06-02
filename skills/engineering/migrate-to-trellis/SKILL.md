---
name: migrate-to-trellis
description: >
  Plans a migration from dev-skills Rust workflow artifacts to Trellis beta while preserving ADRs,
  architecture docs, repo rules, and useful historical evidence. Use when adopting Trellis for an
  existing repo with AGENTS.md, CONTEXT.md, docs/adr, docs/architecture, docs/workstreams, or old
  dev-skills workstream state, especially when workstreams should be archived or replaced by
  Trellis tasks and specs.
---

# Migrate To Trellis

Use Trellis as the workflow runtime. Treat legacy dev-skills artifacts as project knowledge to
preserve, convert, archive, or delete from active authority.

## Quick Start

1. Read `references/trellis-essence.md` before planning the migration.
2. Read Trellis local truth in the target repo if installed: `.trellis/workflow.md`,
   `.trellis/config.yaml`, `.trellis/spec/`, `.trellis/tasks/`, and Trellis agent instructions.
3. Run the bundled read-only audit. It also reports legacy skill/workstream references in active
   docs so they can be cleaned after migration.

   ```powershell
   python skills\engineering\migrate-to-trellis\scripts\audit_trellis_migration.py <repo> --format text
   ```

4. Produce a migration plan before moving files. Do not delete or rewrite historical docs in the
   first pass.

## Example

```text
User: Migrate this repo from the old workstream docs to Trellis.
Assistant: Audit AGENTS.md, CONTEXT.md, docs/workstreams, and existing Trellis files; then propose
which workstreams become Trellis tasks and which legacy files should be archived or removed.
```

## Migration Rules

- Trellis owns active workflow state: task lifecycle, PRDs, implement/check context manifests,
  workspace memory, workflow-state breadcrumbs, hooks, and finish/check loops.
- Keep durable architecture knowledge: `docs/adr/**`, `docs/architecture/**`, repo-specific
  `AGENTS.md` rules, and stable parts of `CONTEXT.md`.
- Convert active or genuinely current workstreams into Trellis tasks only when they still represent
  live work. Seed `prd.md`, `implement.jsonl`, `check.jsonl`, and optional `research/`.
- Retire closed, completed, abandoned, or stale workstreams after extracting durable knowledge. Do
  not keep a large legacy workstream tree unless the user explicitly wants an audit archive.
- Drop machine ledgers as workflow authority after migration: old `TASKS.jsonl`, `CAMPAIGNS.jsonl`,
  generated handoff queues, and workstream status files must not compete with Trellis task state.
- Preserve evidence that explains architecture decisions, validation gates, or regression risks by
  summarizing or linking it into Trellis task `research/` or `.trellis/spec/guides/`.

## Mapping

For detailed artifact treatment, read `references/mapping.md`.

Core mapping:

- `docs/adr/**` -> keep in place; reference from Trellis specs/tasks.
- `docs/architecture/**` -> keep in place or summarize into `.trellis/spec/guides/architecture.md`.
- `CONTEXT.md` -> distill stable domain language into `.trellis/spec/guides/project-context.md`.
- active `docs/workstreams/<slug>/` -> convert to one Trellis task or parent task with subtasks.
- closed workstreams -> extract durable lessons, then remove from active docs or move to a legacy
  archive only if explicitly requested.
- validation commands -> move into Trellis spec quality checks or task `check.jsonl` reasons.
- code paths -> do not put them in `implement.jsonl` / `check.jsonl`; agents discover code from the
  PRD and specs.

## Process

1. Audit current state with the bundled script and `git status`.
2. Decide whether Trellis is already installed. If not, ask the user to confirm Trellis beta init
   before running install/init commands.
3. Create a migration task in Trellis for the conversion work.
4. Preserve ADR and architecture docs first; do not flatten them into PRD prose.
5. Convert only current work into Trellis tasks. Keep each task small enough for implement/check
   agents to own.
6. Curate `implement.jsonl` and `check.jsonl` with exact source files, specs, ADRs, and research.
7. Leave an explicit archive note for old workstream directories that are retained only as history.

## Output

Report:

- Trellis installation status,
- docs to keep, convert, archive, or ignore,
- active docs that still reference retired skills or workstream files,
- active workstreams that should become Trellis tasks,
- stale workstreams that should not be assignable,
- spec files to create under `.trellis/spec/`,
- context entries to add to `implement.jsonl` and `check.jsonl`,
- and any user decisions needed before moving or deleting files.

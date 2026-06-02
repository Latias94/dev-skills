# Dev Skills Context

## Current Direction

This repository is no longer the source of a Rust workstream workflow. Trellis beta should own active
development workflow, task state, subagent dispatch, context injection, and finish/check loops.

This repository keeps only small reusable Codex skills and a migration helper.

## Retained Local Skills

- `commit-work`
- `codex-session-recovery`
- `humanizer`
- `migrate-to-trellis`

Matt-style engineering skills are expected to be installed outside this repository.

## Migration Vocabulary

**Trellis task**
: A short-lived unit of work under `.trellis/tasks/<task>/` with `prd.md`, optional `research/`,
`implement.jsonl`, `check.jsonl`, and `task.json`.

**Trellis spec**
: Durable executable project knowledge under `.trellis/spec/`. Specs should contain reusable
implementation rules, quality checks, contracts, and gotchas.

**Legacy workstream**
: A retired dev-skills workflow directory. It should not remain active workflow state after
migration. Convert only live work into Trellis tasks; extract useful lessons from closed
workstreams and retire the rest.

## Source Of Truth Order After Migration

1. Trellis workflow and task state for active work
2. ADRs and architecture docs for durable decisions
3. Trellis specs for executable project knowledge
4. Task research files for one-off investigation
5. Chat history

## Avoid

- Recreating old workstream queues inside Trellis.
- Keeping legacy machine ledgers as active authority.
- Copying every historical workstream into `.trellis/tasks/`.
- Putting source-code paths into Trellis `implement.jsonl` or `check.jsonl`.

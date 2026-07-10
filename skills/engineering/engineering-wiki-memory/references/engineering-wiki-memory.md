# Engineering Wiki Memory Reference

## Format

Engineering memory is an OKF-compatible directory of UTF-8 Markdown concepts with YAML frontmatter. Every
non-reserved concept has a non-empty `type`. Standard OKF fields are `title`, `description`, `resource`,
`tags`, and `timestamp`; consumers tolerate unknown fields, missing optional fields, missing indexes, and
broken links.

`index.md` and `log.md` are reserved filenames. They are optional navigation and history views, not canonical
facts. Normal cross-links should be bundle-relative Markdown links where practical.

## Canonical Order

1. Immutable concept shards are canonical facts.
2. Registration snapshots publish lane identity and state lineage.
3. `current-state.md` and root `log.md` are deterministic materialized views.
4. `index.md` is stable navigation for progressive disclosure.

The supporting concurrent protocol is in [concurrent-writes.md](concurrent-writes.md).

## Layout

```text
docs/knowledge/engineering/
├── index.md
├── current-state.md
├── log.md
├── decisions/YYYY-MM/
├── progress/YYYY-MM/
├── registry/YYYY-MM/
├── sessions/YYYY-MM/
├── subagents/YYYY-MM/
├── verification/YYYY-MM/
├── logs/YYYY-MM/
├── conventions/YYYY-MM/
└── legacy/YYYY-MM/
```

Use only useful directories. A small repository may keep few concepts, but a parallel repository should retain
`registry/`, `progress/`, `sessions/`, `verification/`, and `logs/` as immutable write targets.

## Concept Metadata

All new shards receive:

```yaml
type: Work Progress
title: Scheduler refactor progress
description: One-line durable summary.
timestamp: 2026-07-10T03:14:56Z
record_id: 6c1e2ec7ec7f4e23af911d8bbd6c50ed
producer_id: codex-laptop-a
run_id: session-019ec1da
```

Useful optional fields include `source_session`, `subagent_id`, `related_plan`, `related_issue`, `git_branch`,
`git_commit`, `verified_by`, and `supersedes`. Unknown keys remain non-authoritative hints.

`Work Registration` additionally needs a stable `registration_id`; its `supersedes` field references the prior
registration snapshot's `record_id` when state changes and must remain in the same registration lineage. Use
`external_runtime` to reference a repo-relative mutable workstream manifest without copying its live state;
successor snapshots inherit that association.

## Recommended Types

- `Work Registration`: immutable identity or state snapshot for a producer, development context, or lane.
- `Work Progress`: implementation progress tied to a plan, issue, branch, or commit.
- `Session Handoff`: context needed after compaction, interruption, or a new session.
- `Decision`: durable engineering choice, alternatives, and rationale.
- `Subagent Finding`: distilled independent finding and disposition.
- `Verification Evidence`: test, lint, build, benchmark, or manual result.
- `Memory Event`: compact chronological fact.
- `Legacy Rollup Snapshot`: immutable capture created before explicit adoption replaces a human-maintained root view.
- `Repo Convention` and `Skill Contract`: durable local guidance.

## Body Shapes

Use structural Markdown and include only sections that add evidence. These conventional shapes make retrieval
predictable without turning OKF into a fixed schema.

`Work Registration`:

```md
# Scope

# Current Claim

# Latest Links

# Handoff

# Citations
```

`Session Handoff`:

```md
# Summary

# Verified State

# Open Threads

# Next Action

# Citations
```

`Decision`:

```md
# Decision

# Context

# Alternatives

# Consequences

# Citations
```

`Verification Evidence`:

```md
# Verification

# Result

# Evidence

# Follow-up

# Citations
```

## Validation

`validate` fails for missing concept types, duplicate `record_id` values, and unresolved Git conflict markers.
It warns about stale rollups, legacy concepts without `record_id`, malformed registration lineage, oversized
rollups, local absolute paths, external workstream runtimes, and historical mutable ledgers. Active external
workstreams that have no open `external_runtime` registration and are older than 30 days are advisory drift
signals. A legacy root
rollup without the derived marker is reported separately from a stale derived view and cannot be overwritten by
normal `render`; use explicit `--adopt-rollups` to preserve it as an immutable snapshot first. Warnings are
non-destructive migration guidance.

## Relationship To Plans

Plans remain decision artifacts. Register the active context with `related_plan`, then put progress, final gates,
post-merge revalidation, and handoffs into memory shards. Preserve old plan progress files as history; do not add
new mutable execution ledgers to `docs/plans/`. Existing `docs/workstreams` manifests remain their own mutable
workflow runtime: cite them from a registration shard rather than copying their live state into memory.

## Sources

- Google Cloud, [How the Open Knowledge Format can improve data sharing](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing/)
- GoogleCloudPlatform, [Open Knowledge Format v0.1 draft specification](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)

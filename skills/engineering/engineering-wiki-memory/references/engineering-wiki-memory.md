# Engineering Wiki Memory Reference

Use this reference when creating or maintaining repo-local engineering memory.

## Source Format

Use an OKF-compatible shape: a directory tree of UTF-8 Markdown files with YAML frontmatter. Non-reserved concept files require a non-empty `type` field. Recommended optional fields include `title`, `description`, `resource`, `tags`, and `timestamp`.

Reserved filenames:

- `index.md`: directory listing for progressive disclosure.
- `log.md`: chronological update history.

Consumers should tolerate unknown types, unknown frontmatter keys, broken links, missing optional fields, and missing indexes. Keep the bundle useful even when partially generated.

## Recommended Layout

```text
docs/knowledge/engineering/
├── index.md
├── log.md
├── current-state.md
├── decisions/
├── progress/
├── sessions/
├── subagents/
├── verification/
└── conventions/
```

Use only the directories that help the current repository. A small repo may keep all concepts at the root.

## Concept Types

Use descriptive type values. Recommended engineering types:

- `Current State`: the shortest durable summary of what is true now.
- `Work Progress`: implementation progress tied to a plan, issue, branch, or commit.
- `Session Handoff`: context needed after compaction, interruption, or a new Codex session.
- `Decision`: a durable engineering choice with alternatives and rationale.
- `Subagent Finding`: distilled output from a spawned agent or independent review.
- `Verification Evidence`: test, lint, build, benchmark, or manual verification result.
- `Repo Convention`: local rule or repeated pattern that future agents should follow.
- `Skill Contract`: how a local skill or workflow should be invoked.

Custom frontmatter keys are allowed. Useful producer-defined keys:

```yaml
status: active
source_session: 019ec1da-c8f4-7e93-9bc2-e445d33e5506
subagent_id: 019ec3a6-147c-7aa1-a910-40ac2a984c75
related_plan: docs/plans/2026-06-13-003-refactor-cailun-architecture-hardening-plan.md
git_branch: feat/pdf-compat-jpx
git_commit: abc1234
verified_by: cargo nextest run -p cailun-scheduler
```

Unknown keys must remain non-authoritative hints.

## Body Shapes

`Current State`:

```md
# Current State

- Goal:
- Branch:
- Last verified:
- Done:
- In progress:
- Blocked:
- Next action:

# Citations

[1] [Plan](../plans/example.md)
```

`Session Handoff`:

```md
# Summary

# Verified State

# Open Threads

# Next Action

# Citations
```

`Subagent Finding`:

```md
# Finding

# Evidence

# Recommendation

# Disposition
```

`Decision`:

```md
# Decision

# Context

# Alternatives

# Consequences

# Citations
```

## Write Triggers

Write or update memory at these boundaries:

- Before or after a long-context compaction.
- After a subagent finishes with reusable findings.
- After a commit that changes architecture, contract, tests, or task direction.
- After a failed or aborted long run if continuation would otherwise depend on chat history.
- When a decision changes implementation direction.
- When verification proves or disproves a plan assumption.

Do not write memory for tiny local edits whose state is obvious from git.

## Reading Order For Agents

When resuming work:

1. Read `index.md`.
2. Read `current-state.md` if present.
3. Read the relevant `log.md` section for recent updates.
4. Read only concepts linked from the current task.
5. Verify against git, files, tests, and current user instructions before acting.

## Relationship To Plans And CE

Compound Engineering plans remain decision artifacts. Do not add checkboxes or execution state to plan bodies unless the user explicitly requests it. Engineering wiki memory is the sidecar for execution continuity, subagent findings, and compaction recovery.

This replaces the useful part of old workstream handoffs without reintroducing planner-owned ledgers, task queues, or conflicting state authorities.

## Sources

- Google Cloud, "How the Open Knowledge Format can improve data sharing": https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing/
- OKF v0.1 draft specification: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md

# Engineering Wiki Memory Reference

Use this reference when creating or maintaining repo-local engineering memory.

## Source Format

Use an OKF-compatible shape: a directory tree of UTF-8 Markdown files with YAML frontmatter. Non-reserved concept files require a non-empty `type` field. Recommended optional fields include `title`, `description`, `resource`, `tags`, and `timestamp`.

Reserved filenames:

- `index.md`: directory listing for progressive disclosure.
- `log.md`: chronological update history.

Consumers should tolerate unknown types, unknown frontmatter keys, broken links, missing optional fields, stale rollups, and missing indexes. Keep the bundle useful even when partially generated.

## Concurrent Memory Model

Use this source-of-truth order:

1. Sharded concept files are canonical facts.
2. `registry/` publishes active producers, development contexts, and agent lanes.
3. `current-state.md`, root `log.md`, and `index.md` are materialized views.

Use append-only sharding for normal agent writes:

- Create a new concept file for each handoff, progress update, verification result, subagent finding, and log event.
- Use unique filenames by default: UTC timestamp plus a slug. Use `--path` only when a stable human-named file is worth the merge risk.
- Do not overwrite another producer's concept. Create a successor concept and cite the older one.
- Create or update one `Work Registration` per active parallel unit in `registry/`.
- Treat `current-state.md`, root `log.md`, and `index.md` as shared rollup views. They may lag and may be rebuilt from sharded concepts and registrations.
- If a rollup conflicts, keep the concept files and regenerate or manually reconcile the rollup. The concepts are the source of truth.

This keeps the OKF benefits of plain Markdown, YAML metadata, links, and git diffs while avoiding hot files that every computer or agent edits at the same time.

## Rollup Budgets

Rollups should stay small enough to read before work starts:

- `current-state.md`: active registrations, a short integrated summary, and next action only.
- `log.md`: recent digest entries, not a complete event log.
- `index.md`: sparse navigation and the most useful active links, not a full catalog of every concept.

If a rollup grows large or conflicts often, freeze it as a historical rollup, create fresh sharded concepts for new facts, and rebuild the rollup during an integration pass. Do not keep appending execution evidence to a hot rollup because it is already there.

## Existing Bundle Migration

Migrate existing engineering memory incrementally:

1. Run `init` against the existing root. It creates missing directories without overwriting existing `index.md`, `log.md`, or `current-state.md`.
2. Keep existing `current-state.md` and `log.md` as historical rollups. Do not rewrite them into the new model unless you are already resolving a conflict.
3. Add `registry/` entries for currently active producers, development contexts, or agent lanes.
4. Treat old per-plan progress ledgers as historical rollups. Write future progress as new timestamped `Work Progress` concepts and link them from the registration or latest rollup.
5. Leave old workstream/task-runtime directories in place as archives. Read them as citations when relevant, but do not recreate their mutable queues, ledgers, or `WORKSTREAM.json` runtime.
6. Write new progress, handoff, verification, and log facts as sharded concepts.
7. During the next integration pass, refresh `current-state.md` and `log.md` from recent registrations and sharded facts.

This preserves old links and Git history while moving future writes away from shared hot files.

## Validation Warnings

`validate` should stay permissive for OKF compatibility. It may warn about:

- Missing `registry/` in a bundle used for parallel work.
- Oversized `current-state.md`, `log.md`, or `index.md` rollups.
- `current-state.md` branch metadata that differs from the checked-out Git branch.
- Local absolute paths outside `source_workspace` hints.
- Large mutable progress files that look like per-plan ledgers.
- Historical progress or audit documents under `docs/plans/`.

Warnings are migration signals, not hard conformance errors. Fix them by moving future writes into
sharded concepts, registering active contexts, and refreshing rollups during integration.

## Recommended Layout

```text
docs/knowledge/engineering/
├── index.md
├── log.md
├── current-state.md
├── decisions/
├── progress/
├── registry/
├── sessions/
├── subagents/
├── verification/
├── logs/
└── conventions/
```

Use only the directories that help the current repository. A small repo may keep all concepts at the root. In a multi-agent repo, keep `registry/`, `logs/`, `sessions/`, and `progress/` as sharded write targets even if root rollups are sparse.

## Concept Types

Use descriptive type values. Recommended engineering types:

- `Current State`: the shortest integrated summary of what is true now; usually a cached rollup.
- `Work Registration`: active or recently active producer, development context, or agent lane.
- `Work Progress`: implementation progress tied to a plan, issue, branch, or commit.
- `Session Handoff`: context needed after compaction, interruption, or a new Codex session.
- `Decision`: a durable engineering choice with alternatives and rationale.
- `Subagent Finding`: distilled output from a spawned agent or independent review.
- `Verification Evidence`: test, lint, build, benchmark, or manual verification result.
- `Memory Event`: append-only chronological event used instead of editing root `log.md`.
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
producer_id: codex-laptop-a
source_workspace: F:\SourceCodes\Rust\fret
last_seen: 2026-07-04T03:14:56Z
```

Unknown keys must remain non-authoritative hints.

## Body Shapes

`Current State`:

```md
# Current State

- Snapshot timestamp:
- Goal:
- Last verified:
- Next action:

# Active Registrations

- [scheduler refactor](registry/scheduler-refactor-codex-laptop-a.md): active

# Integrated Summary

- Done:
- In progress:
- Blocked:

# Citations

[1] [Plan](../plans/example.md)
```

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

`Memory Event`:

```md
# Event

# Impact

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
- When multiple agents or machines are active and a shared rollup would otherwise be edited.
- When a producer, development context, or agent lane starts, pauses, resumes, or finishes.

Do not write memory for tiny local edits whose state is obvious from git.

## Reading Order For Agents

When resuming work:

1. Read `index.md`.
2. Read `current-state.md` if present, treating it as a possibly stale rollup.
3. Read relevant active or recent registrations in `registry/`.
4. Scan recent sharded concepts in `sessions/`, `progress/`, `verification/`, `subagents/`, and `logs/` by timestamp.
5. Read the relevant `log.md` section only if the repository maintains a rollup.
6. Read only concepts linked from the current task.
7. Verify against git, files, tests, and current user instructions before acting.

## Relationship To Plans And CE

Compound Engineering plans remain decision artifacts. Do not add checkboxes or execution state to plan bodies unless the user explicitly requests it. Engineering wiki memory is the sidecar for execution continuity, subagent findings, and compaction recovery.

When using `ce-plan`:

- Register the active development context with `related_plan` pointing at the implementation-ready plan.
- Keep CE plan files in `docs/plans/` focused on WHAT/HOW decisions, requirements, implementation units, and verification contract.
- Record execution progress, final gates, post-merge revalidation, and next-action handoffs as memory concepts instead of editing the plan body.
- If old `docs/plans/*progress*.md` or audit files exist, treat them as historical artifacts. Do not create new progress documents in `docs/plans/`; use `docs/knowledge/engineering/progress/` or `verification/`.
- In `current-state.md`, link the active registration or plan once. Do not copy large plan sections or full verification transcripts into the rollup.

This replaces the useful part of old workstream handoffs without reintroducing planner-owned ledgers, task queues, or conflicting state authorities.

## Sources

- Google Cloud, "How the Open Knowledge Format can improve data sharing": https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing/
- OKF v0.1 draft specification: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md

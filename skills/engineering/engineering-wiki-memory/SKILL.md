---
name: engineering-wiki-memory
description: Create and maintain sparse, OKF-compatible engineering memory for resumable work. Use when continuity must survive compaction, handoff, parallel work, or a later session.
---

# Engineering Wiki Memory

Use this skill for **continuity evidence**, not as a replacement for architecture docs,
plans, workstream runtimes, or a general project knowledge base.

Read [the reference](references/engineering-wiki-memory.md) before creating or migrating a
bundle. Read [the concurrent-write protocol](references/concurrent-writes.md) when more than
one producer can write the bundle.

## Operating policy

- Capture one immutable shard only when it changes what a later agent should do.
- Prefer one complete handoff, decision, or verification record over per-command or per-turn notes.
- Register a lane only for durable parallel context; create successors for meaningful state changes,
  not every progress update.
- Use `log` only for lifecycle events such as creation, deprecation, supersession, regeneration,
  migration, or verification. Routine checks stay in the source shard and do not enter `log.md`.
- Keep raw logs, command output, TODO queues, and mutable `WORKSTREAM.json` files outside the bundle.
- Keep product and architecture authority in its owning documents; cite those documents from memory.

## Record selection

| Situation | Record type |
| --- | --- |
| Context boundary or restart | `Session Handoff` |
| Durable design choice | `Decision` |
| Meaningful implementation checkpoint | `Work Progress` |
| Reusable finding from another agent | `Subagent Finding` |
| Test, build, benchmark, or manual gate | `Verification Evidence` |
| Parallel lane identity or state transition | `Work Registration` |
| Explicit lifecycle event | `Memory Event` via `log` |

## Setup and capture

```text
python <skill-root>/scripts/wiki_memory.py init --root docs/knowledge/engineering
python <skill-root>/scripts/wiki_memory.py new --root docs/knowledge/engineering --type "Verification Evidence" --title "Focused gate" --git-commit <sha>
```

For a parallel lane, give it one stable identity and link the external runtime instead of copying it:

```text
python <skill-root>/scripts/wiki_memory.py register --root docs/knowledge/engineering --title "Scheduler refactor" --registration-id codex-scheduler --producer-id codex-laptop --external-runtime docs/workstreams/scheduler/WORKSTREAM.json
```

After integrating shards, one owner refreshes the shared views:

```text
python <skill-root>/scripts/wiki_memory.py render --root docs/knowledge/engineering --check
python <skill-root>/scripts/wiki_memory.py render --root docs/knowledge/engineering --owner codex-laptop
python <skill-root>/scripts/wiki_memory.py validate --root docs/knowledge/engineering
```

## Existing repositories

Do not backfill every Markdown file in a large repository. Keep existing plans, ADRs, guides,
workstreams, and historical reports where they already have authority. Add a small curated OKF
knowledge bundle only when consumers need concept-level discovery; add `index.md` progressively and
use `generated`, `verified`, `status`, `stale_after`, and `sources` when those signals are known.

If an existing memory directory contains noisy or legacy shards, preserve them as history. First
rerender the derived views with the sparse policy; review or archive old shards in a separate,
explicit repository change. This skill never deletes history automatically.

```text
Use $engineering-wiki-memory to capture one verified handoff, not a log entry for every command.
```

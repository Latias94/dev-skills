---
name: engineering-wiki-memory
description: Engineering memory for resumable repo state. Use when continuity must survive compaction, handoff, parallel work, or a later session.
---

# Engineering Wiki Memory

Capture volatile state as an OKF-compatible bundle: **immutable shards, derived rollups**.

Read [the reference](references/engineering-wiki-memory.md) before creating or migrating a bundle.
For multi-machine work, read [the concurrent-write protocol](references/concurrent-writes.md).

## Setup

```sh
python "${CODEX_HOME:-$HOME/.codex}/skills/engineering-wiki-memory/scripts/wiki_memory.py" init --root docs/knowledge/engineering
```

## Normal Capture

```sh
python "${CODEX_HOME:-$HOME/.codex}/skills/engineering-wiki-memory/scripts/wiki_memory.py" new \
  --root docs/knowledge/engineering \
  --type "Session Handoff" \
  --title "Scheduler identity handoff" \
  --producer-id codex-laptop-a \
  --run-id session-019ec1da
```

Use `log` for a short chronological fact:

```sh
python "${CODEX_HOME:-$HOME/.codex}/skills/engineering-wiki-memory/scripts/wiki_memory.py" log \
  --root docs/knowledge/engineering \
  --kind "Verification" \
  --producer-id codex-laptop-a \
  "cargo nextest passed for cailun-scheduler"
```

## Parallel Capture

Give every concurrent lane a stable global `registration_id`; identify its producer separately:

```sh
python "${CODEX_HOME:-$HOME/.codex}/skills/engineering-wiki-memory/scripts/wiki_memory.py" register \
  --root docs/knowledge/engineering \
  --title "Scheduler refactor" \
  --registration-id codex-laptop-a-scheduler-refactor \
  --producer-id codex-laptop-a \
  --external-runtime docs/workstreams/scheduler-refactor/WORKSTREAM.json \
  --git-branch feat/scheduler-refactor \
  --related-plan docs/plans/2026-07-04-scheduler-refactor-plan.md
```

Change lane state with a successor snapshot using `--supersedes <prior-record-id>`; repeat it to resolve heads.

## Integration And Resume

After pulling or rebasing all relevant shards, check rollups without writing:

```sh
python "${CODEX_HOME:-$HOME/.codex}/skills/engineering-wiki-memory/scripts/wiki_memory.py" render \
  --root docs/knowledge/engineering --check
```

A single integration owner resolves competing registration heads, then renders shared views:

```sh
python "${CODEX_HOME:-$HOME/.codex}/skills/engineering-wiki-memory/scripts/wiki_memory.py" render \
  --root docs/knowledge/engineering --owner codex-laptop-a
```

Human-maintained root views require one explicit adoption; it snapshots them under `legacy/` first:

```sh
python "${CODEX_HOME:-$HOME/.codex}/skills/engineering-wiki-memory/scripts/wiki_memory.py" render \
  --root docs/knowledge/engineering --owner codex-laptop-a --adopt-rollups
```

Validate before relying on it:

```sh
python "${CODEX_HOME:-$HOME/.codex}/skills/engineering-wiki-memory/scripts/wiki_memory.py" validate --root docs/knowledge/engineering
```

## Capture Rules

- Capture at context boundaries: compaction, plan, decision, commit, verification, blocker, return, or handoff.
- Cite plans, issue IDs, commits, test commands, session IDs, and local documents rather than copying raw logs.
- Keep memory as continuity evidence. Use a tracker or Codex threads for real-time task claiming.
- Treat `docs/workstreams` manifests and `TODO`/`HANDOFF` files as external mutable runtimes; only link them.
- Store no secrets, credentials, private tokens, or full command output.
- Treat plans as decision artifacts; keep execution continuity in the memory bundle.

```text
Use $engineering-wiki-memory to register one parallel lane and capture its verified handoff as immutable shards.
```

# Dev Skills

This repository keeps a small personal Codex skill set.

Compound Engineering is the preferred engineering workflow. Keep it installed as the external
plugin, and use this repository for local utility skills plus a curated vendored copy of Matt
Pocock's daily engineering and productivity skills.

The previous Rust workstream, Loom, and Project Compass workflows are retired. Do not recreate a
parallel planning or lane runtime here.

## Default Stack

```text
Compound Engineering plugin -> Matt Pocock skills -> local utility skills
```

- **Compound Engineering** owns strategy, brainstorm, planning, execution, review, and knowledge
  capture. It is installed as a Codex plugin, not vendored into this repository.
- **Matt Pocock skills** provide small composable workflows for alignment, TDD, diagnosis,
  architecture improvement, PRDs, issue slicing, teaching, and handoffs.
- **last30days** provides recency-oriented social and web research across Reddit, X, YouTube,
  TikTok, Hacker News, Polymarket, GitHub, and web sources.
- **Local utility skills** cover personal closeout, session recovery, engineering wiki memory,
  prose cleanup, and logo generation.

## Managed Skills

Local utility skills:

- [`commit-work`](./skills/engineering/commit-work/SKILL.md) — create safe reviewable git commits.
- [`codex-session-recovery`](./skills/engineering/codex-session-recovery/SKILL.md) — recover
  actionable context from Codex session files.
- [`codex-subagent-cleanup`](./skills/engineering/codex-subagent-cleanup/SKILL.md) — find stale
  Codex subagent handles that can be closed with `close_agent`.
- [`engineering-wiki-memory`](./skills/engineering/engineering-wiki-memory/SKILL.md) — maintain a
  repo-local wiki memory bundle for session handoffs, decisions, subagent findings, and
  verification evidence.
- [`humanizer`](./skills/misc/humanizer/SKILL.md) — make prose sound more natural while preserving
  facts and terminology.
- [`logo-generator`](./skills/misc/logo-generator/SKILL.md) — generate SVG logo concepts, PNG
  exports, and polished showcase pages or images.

Vendored Matt Pocock engineering skills:

- [`diagnose`](./skills/engineering/diagnose/SKILL.md)
- [`grill-with-docs`](./skills/engineering/grill-with-docs/SKILL.md)
- [`improve-codebase-architecture`](./skills/engineering/improve-codebase-architecture/SKILL.md)
- [`prototype`](./skills/engineering/prototype/SKILL.md)
- [`setup-matt-pocock-skills`](./skills/engineering/setup-matt-pocock-skills/SKILL.md)
- [`tdd`](./skills/engineering/tdd/SKILL.md)
- [`to-issues`](./skills/engineering/to-issues/SKILL.md)
- [`to-prd`](./skills/engineering/to-prd/SKILL.md)
- [`triage`](./skills/engineering/triage/SKILL.md)
- [`zoom-out`](./skills/engineering/zoom-out/SKILL.md)

Vendored Matt Pocock productivity skills:

- [`caveman`](./skills/productivity/caveman/SKILL.md)
- [`grill-me`](./skills/productivity/grill-me/SKILL.md)
- [`handoff`](./skills/productivity/handoff/SKILL.md)
- [`teach`](./skills/productivity/teach/SKILL.md)
- [`write-a-skill`](./skills/productivity/write-a-skill/SKILL.md)

Vendored research skills:

- [`last30days`](./skills/research/last30days/SKILL.md) — research what people actually said about
  a topic in the last 30 days. It includes its upstream engine scripts and optional API-key backed
  source integrations.

Vendored misc skills:

- [`logo-generator`](./skills/misc/logo-generator/SKILL.md) — create product or brand logo variants
  with bundled design references, SVG/PNG export scripts, and showcase templates.

Each vendored upstream skill includes `SOURCE.md` with repository, path, license, synced ref, and
sync time.

## Install

Install the managed local skills into Codex:

```powershell
python scripts\install_dev_skills.py --force
```

The installer also removes obsolete managed skills listed in `skills.json` under `remove.skills`.
That cleanup list includes the retired Loom, Project Compass, workstream, and zero-use optional
skills. It does not delete the Compound Engineering plugin cache.

Install or refresh the recommended Compound Engineering external workflow outside this installer.
Keep CE as an external Codex plugin so the local skill installer never modifies Codex plugin
marketplaces, plugin cache, or companion agent state.

## Upstream Skill Sync

`upstream-skills.json` records the upstream source for vendored skills and tracks the external CE
plugin as the preferred source for `ce-*` skills.

Use dry-run mode before writing:

```powershell
python scripts\sync_upstream_skills.py --list
python scripts\sync_upstream_skills.py
python scripts\sync_upstream_skills.py --write --force
```

The sync script records upstream repository URL, license, upstream path, ref, and sync time in each
vendored skill's `SOURCE.md`.

## Cleanup Policy

- Keep Compound Engineering installed as a plugin; do not vendor individual `ce-*` skill bodies.
- Use engineering wiki memory bundles for durable agent continuity instead of reviving retired workstream
  ledgers.
- Keep Matt Pocock's current recommended skills vendored when they are small and composable.
- Remove retired Loom, Project Compass, workstream, and Trellis-style workflow skills.
- Remove optional standalone skills that have no recent usage unless there is a clear reason to keep
  them.
- Do not add Claude plugin metadata unless explicitly requested.
- Do not commit changes unless the user confirms.

## Validation

```powershell
python scripts\validate_skills.py
```

The validator applies the strict local authoring checklist to local skills. Vendored upstream skills
are validated for required frontmatter and source attribution without rewriting their upstream
structure.

# Dev Skills

This repository now keeps a small personal Codex skill set and a Trellis migration helper.

The previous Rust workstream / upper-planner workflow has been retired. Use Trellis beta for active
task workflow, subagent dispatch, task context, workspace memory, and finish/check loops.

## Retained Skills

- [`commit-work`](./skills/engineering/commit-work/SKILL.md) — create safe reviewable git commits.
- [`codex-session-recovery`](./skills/engineering/codex-session-recovery/SKILL.md) — recover context
  from Codex session files.
- [`humanizer`](./skills/misc/humanizer/SKILL.md) — make prose sound more natural.
- [`migrate-to-trellis`](./skills/engineering/migrate-to-trellis/SKILL.md) — audit legacy
  dev-skills/workstream docs and plan migration to Trellis.

Matt Pocock-style skills such as `diagnose`, `tdd`, `triage`, `to-prd`, `to-issues`,
`improve-codebase-architecture`, and `zoom-out` are expected to live in the user's installed skill
set rather than this repository.

## Install

Install the retained local skills and selected Matt Pocock skills into Codex:

```powershell
python scripts\install_dev_skills.py --force
```

The installer also removes obsolete managed skills listed in `skills.json` under `remove.skills`.
Restart Codex after installing or updating skills.

## Migration Direction

Use Trellis as the workflow runtime:

- `.trellis/workflow.md` owns phase routing and per-turn workflow-state breadcrumbs.
- `.trellis/tasks/<task>/` owns one unit of work: `prd.md`, `research/`, `implement.jsonl`,
  `check.jsonl`, and `task.json`.
- `.trellis/spec/` owns reusable project knowledge and quality checks.
- Trellis implement/check/research agents own isolated execution.

Keep durable project docs:

- ADRs
- architecture maps
- stable repo rules
- validation conventions that should become Trellis specs

Retire legacy workstream queues:

- Convert only live workstreams into Trellis tasks.
- Extract useful lessons from closed workstreams, then remove them from active docs.
- Do not keep legacy machine ledgers as workflow authority.

## Migration Audit

Run the read-only audit helper from this repo:

```powershell
python skills\engineering\migrate-to-trellis\scripts\audit_trellis_migration.py <repo> --format text
```

The script reports Trellis install status, ADR/architecture docs to keep, live workstreams to convert,
stale workstreams to retire, and references to legacy workflow files.

## Repository Policy

- Repository docs and skill bodies are written in English.
- Do not reintroduce a competing workstream workflow here.
- Prefer Trellis for active project workflow and this repo for small reusable helper skills.

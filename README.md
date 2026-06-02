# Dev Skills

This repository keeps a small personal Codex skill set.

The previous Rust workstream / upper-planner workflow has been retired. Use Trellis beta for active
task workflow, subagent dispatch, task context, workspace memory, and finish/check loops.

## Retained Skills

- [`commit-work`](./skills/engineering/commit-work/SKILL.md) — create safe reviewable git commits.
- [`codex-session-recovery`](./skills/engineering/codex-session-recovery/SKILL.md) — recover context
  from Codex session files.
- [`humanizer`](./skills/misc/humanizer/SKILL.md) — make prose sound more natural.

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

## Repository Policy

- Repository docs and skill bodies are written in English.
- Do not reintroduce a competing workstream workflow here.
- Prefer Trellis for active project workflow and this repo for small reusable helper skills.

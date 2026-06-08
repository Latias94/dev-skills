# Dev Skills Context

## Current Direction

This repository is no longer the source of a heavy Rust workstream workflow. It now owns a lightweight
adapter layer around Compound Engineering:

- `project-compass` adapts legacy/local project memory into CE.
- `loom` routes older Loom requests to CE, supplies local safety constraints, and falls back to lane
  discovery only when CE is unavailable or unsuitable.

This repository keeps only small reusable Codex skills.

## Retained Local Skills

- `commit-work`
- `codex-session-recovery`
- `project-compass`
- `loom`
- `humanizer`

External engineering skills are optional. Vendor them only when their upstream URL, license, and
update path are recorded.

Compound Engineering is the preferred external workflow. Prefer installing the full plugin and agent
set over vendoring individual `ce-*` skills.

## Avoid

- Recreating old workstream queues or a heavyweight workflow runtime.
- Keeping legacy machine ledgers as active authority.
- Creating a second direction or roadmap workflow beside CE.
- Treating external skills as implicit dependencies.

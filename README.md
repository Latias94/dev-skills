# Dev Skills

This repository keeps a small personal Codex skill set.

Compound Engineering is the preferred engineering workflow. Keep it installed as the external
plugin, and use this repository for local utility skills plus a curated vendored copy of Matt
Pocock's current engineering and productivity skills.

The previous Rust workstream, Loom, and Project Compass workflows are retired. Do not recreate a
parallel planning or lane runtime here.

## Default Stack

```text
Compound Engineering plugin -> Matt Pocock skills -> local utility skills
```

- **Compound Engineering** owns strategy, brainstorm, planning, execution, review, and knowledge
  capture. It is installed as a Codex plugin, not vendored into this repository.
- **Matt Pocock skills** provide small composable workflows for alignment, issue slicing,
  implementation, diagnosis, architecture, domain modeling, TDD, conflict resolution, teaching,
  and handoffs.
- **Deep Research skills** provide a Chinese structured research workflow for outlines, item-level
  deep research, and Markdown reports.
- **Design engineering skills** provide animation vocabulary, UI polish guidance, and strict motion
  review based on Emil Kowalski's design engineering philosophy.
- **Local utility skills** cover personal closeout, session recovery, engineering wiki memory,
  release changelogs, and prose cleanup.

## Managed Skills

Local utility skills:

- [`commit-work`](./skills/engineering/commit-work/SKILL.md) — create safe reviewable git commits.
- [`codex-session-recovery`](./skills/engineering/codex-session-recovery/SKILL.md) — recover
  actionable context from Codex session files.
- [`codex-subagent-cleanup`](./skills/engineering/codex-subagent-cleanup/SKILL.md) — find stale
  Codex subagent handles that can be closed with `close_agent`.
- [`engineering-wiki-memory`](./skills/engineering/engineering-wiki-memory/SKILL.md) — maintain a
  sharded OKF-compatible repo-local wiki memory bundle for session handoffs, decisions, subagent
  findings, parallel work registrations, logs, and verification evidence.
- [`repo-changelog`](./skills/engineering/repo-changelog/SKILL.md) — write concise user-facing
  changelogs from verified diffs with linked PRs, issues, and contributor credit.
- [`humanizer`](./skills/misc/humanizer/SKILL.md) — make prose sound more natural while preserving
  facts and terminology.

Vendored Matt Pocock engineering skills:

- **User-invoked**
  - [`ask-matt`](./skills/engineering/ask-matt/SKILL.md)
  - [`grill-with-docs`](./skills/engineering/grill-with-docs/SKILL.md)
  - [`triage`](./skills/engineering/triage/SKILL.md)
  - [`improve-codebase-architecture`](./skills/engineering/improve-codebase-architecture/SKILL.md)
  - [`setup-matt-pocock-skills`](./skills/engineering/setup-matt-pocock-skills/SKILL.md)
  - [`to-spec`](./skills/engineering/to-spec/SKILL.md)
  - [`to-tickets`](./skills/engineering/to-tickets/SKILL.md)
  - [`implement`](./skills/engineering/implement/SKILL.md)
  - [`wayfinder`](./skills/engineering/wayfinder/SKILL.md)
- **Model-invoked**
  - [`prototype`](./skills/engineering/prototype/SKILL.md)
  - [`diagnosing-bugs`](./skills/engineering/diagnosing-bugs/SKILL.md)
  - [`research`](./skills/engineering/research/SKILL.md)
  - [`tdd`](./skills/engineering/tdd/SKILL.md)
  - [`domain-modeling`](./skills/engineering/domain-modeling/SKILL.md)
  - [`codebase-design`](./skills/engineering/codebase-design/SKILL.md)
  - [`code-review`](./skills/engineering/code-review/SKILL.md)
  - [`resolving-merge-conflicts`](./skills/engineering/resolving-merge-conflicts/SKILL.md)

Vendored Matt Pocock productivity skills:

- **User-invoked**
  - [`grill-me`](./skills/productivity/grill-me/SKILL.md)
  - [`handoff`](./skills/productivity/handoff/SKILL.md)
  - [`teach`](./skills/productivity/teach/SKILL.md)
  - [`writing-great-skills`](./skills/productivity/writing-great-skills/SKILL.md)
- **Model-invoked**
  - [`grilling`](./skills/productivity/grilling/SKILL.md)

Vendored research skills:

- [`deep-research`](./skills/research/deep-research/SKILL.md) — Chinese deep-research outline generation.
- [`research-add-items`](./skills/research/research-add-items/SKILL.md) — add research objects to
  an existing outline.
- [`research-add-fields`](./skills/research/research-add-fields/SKILL.md) — add field definitions
  to an existing research outline.
- [`research-deep`](./skills/research/research-deep/SKILL.md) — run item-level deep research into
  structured JSON outputs.
- [`research-report`](./skills/research/research-report/SKILL.md) — generate a Markdown report from
  deep research JSON outputs.

Matt's primary-source workflow owns the canonical `research` name. The Chinese outline workflow is
installed as `deep-research` so both can coexist without ambiguous skill discovery.

Vendored optional research skills:

- [`last30days`](./skills/research/last30days/SKILL.md) — research what people actually said about
  a topic in the last 30 days. It remains in the repository for on-demand use and upstream sync, but
  is not installed by the default local skill bundle.

Vendored misc skills:

- [`logo-generator`](./skills/misc/logo-generator/SKILL.md) — create product or brand logo variants
  with bundled design references, SVG/PNG export scripts, and showcase templates.
- [`animation-vocabulary`](./skills/misc/animation-vocabulary/SKILL.md) — map vague animation
  descriptions to precise motion terms.
- [`emil-design-eng`](./skills/misc/emil-design-eng/SKILL.md) — apply Emil Kowalski's UI polish,
  component design, and animation philosophy.
- [`review-animations`](./skills/misc/review-animations/SKILL.md) — review animation and motion
  code against a strict craft bar.

Each vendored upstream skill includes `SOURCE.md` with repository, path, license, synced ref, and
sync time.

## Install

Run commands from the repository root. The module form avoids platform-specific file path
separators. If `python` resolves to Python 3.9 or newer, this command works on every platform:

```shell
python -m scripts.install_dev_skills --force
```

When the `python` command is unavailable, use the platform launcher instead:

```shell
# macOS / Linux
python3 -m scripts.install_dev_skills --force

# Windows PowerShell or cmd
py -3 -m scripts.install_dev_skills --force
```

The installer also removes obsolete managed skills listed in `skills.json` under `remove.skills`.
That cleanup list includes the retired Loom, Project Compass, workstream, and zero-use optional
skills. It does not delete the Compound Engineering plugin cache, and it does not remove optional
vendored skills that are merely absent from the default bundle.

With `--force`, the installer mirrors each managed skill with content-aware updates. Unchanged files
are left untouched so a running Codex app-server does not receive unnecessary `skills/changed`
notifications from delete-and-recopy churn.

Install or refresh the recommended Compound Engineering external workflow outside this installer.
Keep CE as an external Codex plugin so the local skill installer never modifies Codex plugin
marketplaces, plugin cache, or companion agent state.

## Upstream Skill Sync

`upstream-skills.json` records the upstream source for vendored skills and tracks the external CE
plugin as the preferred source for `ce-*` skills.

Use dry-run mode before writing:

```shell
python -m scripts.sync_upstream_skills --list
python -m scripts.sync_upstream_skills
python -m scripts.sync_upstream_skills --write --force
```

The sync script records upstream repository URL, license, upstream path, ref, and sync time in each
vendored skill's `SOURCE.md`. Manifest entries may declare narrow frontmatter, invocation, or text
rewrites for local naming compatibility; declared rewrites fail when their expected upstream text
no longer matches.

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

```shell
python -m scripts.validate_skills
```

The validator applies the strict local authoring checklist to local skills. Vendored upstream skills
are validated for required frontmatter and source attribution without rewriting their upstream
structure.

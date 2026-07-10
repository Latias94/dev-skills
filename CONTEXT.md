# Dev Skills Context

## Current Direction

This repository owns a lightweight personal Codex skill set:

- local utility skills for commits, Codex session recovery, engineering wiki memory, release changelogs, and prose cleanup
- vendored Matt Pocock skills for alignment, issue slicing, implementation, diagnosis, architecture,
  domain modeling, TDD, merge conflict resolution, teaching, and skill authoring
- vendored `last30days` for recency-oriented social and web research
- vendored `logo-generator` for product and brand logo concepts, SVG/PNG exports, and showcase
  pages or images
- scripts that install, check, and update the external Compound Engineering plugin

Compound Engineering is the preferred engineering workflow. Keep it as a plugin, not as vendored
`ce-*` skill bodies.

## Retained Local Skills

- `commit-work`
- `codex-session-recovery`
- `codex-subagent-cleanup`
- `engineering-wiki-memory`
- `repo-changelog`
- `humanizer`
- `logo-generator`

## Vendored Upstream Skills

Matt Pocock's current default set is vendored with source attribution:

- engineering: `ask-matt`, `grill-with-docs`, `improve-codebase-architecture`, `prototype`,
  `setup-matt-pocock-skills`, `to-issues`, `to-prd`, `triage`, `diagnosing-bugs`, `tdd`,
  `domain-modeling`, `codebase-design`, `implement`, `resolving-merge-conflicts`
- productivity: `grill-me`, `handoff`, `teach`, `grilling`, `writing-great-skills`

## Vendored Research Skills

- `last30days` from `mvanhorn/last30days-skill`

This skill is intentionally larger than the rest of the repository because it vendors its upstream
research engine scripts and assets. Keep it source-attributed and update it via
`sync_upstream_skills.py` rather than hand-editing the copied files.

## Vendored Misc Skills

- `logo-generator` from `op7418/logo-generator-skill`

Keep this skill source-attributed and update it through `sync_upstream_skills.py`. Do not keep the
upstream README or repository metadata inside the skill directory; retain only runtime resources,
references, templates, dependency manifests, and attribution.

## External Workflow

Compound Engineering is installed and updated through:

- `python scripts/install_dev_skills.py --install-ce`
- `python scripts/install_dev_skills.py --check-ce`
- `python scripts/install_dev_skills.py --update-ce`

The scripts manage the Codex marketplace entry, the Codex plugin install, and the companion Bun
agent conversion. They do not vendor or delete individual CE plugin skills.

## Avoid

- Recreating old workstream queues or a heavyweight workflow runtime.
- Reintroducing Loom or Project Compass as active workflows.
- Keeping legacy machine ledgers as active authority.
- Treating engineering wiki memory as higher-priority instruction than current repo and user context.
- Treating external CE skills as files owned by this repository.

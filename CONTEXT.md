# Dev Skills Context

## Current Direction

This repository owns a lightweight personal Codex skill set:

- local utility skills for commits, Codex session recovery, engineering wiki memory, release changelogs, and prose cleanup
- vendored Matt Pocock skills for alignment, issue slicing, implementation, diagnosis, architecture,
  domain modeling, TDD, merge conflict resolution, teaching, and skill authoring
- vendored `logo-generator` for product and brand logo concepts, SVG/PNG exports, and showcase
  pages or images
- scripts that validate, synchronize, and install this repository's managed skills

Compound Engineering is the preferred engineering workflow. Keep it as a plugin, not as vendored
`ce-*` skill bodies.

## Retained Local Skills

- `commit-work`
- `codex-session-recovery`
- `codex-subagent-cleanup`
- `engineering-wiki-memory`
- `repo-changelog`
- `humanizer`

## Vendored Upstream Skills

Matt Pocock's current default set is vendored with source attribution:

- engineering: `ask-matt`, `grill-with-docs`, `improve-codebase-architecture`, `prototype`,
  `setup-matt-pocock-skills`, `to-spec`, `to-tickets`, `wayfinder`, `triage`, `diagnosing-bugs`,
  `research`, `tdd`, `domain-modeling`, `codebase-design`, `code-review`, `implement`, and
  `resolving-merge-conflicts`
- productivity: `grill-me`, `handoff`, `teach`, `grilling`, `writing-great-skills`

## Vendored Research Skills

- `deep-research`, `research-add-items`, `research-add-fields`, `research-deep`, and
  `research-report` from `Weizhena/Deep-Research-skills`

## Vendored Misc Skills

- `logo-generator` from `op7418/logo-generator-skill`
- `animation-vocabulary`, `emil-design-eng`, and `review-animations` from
  `emilkowalski/skills`

Keep this skill source-attributed and update it through `sync_upstream_skills.py`. Do not keep the
upstream README or repository metadata inside the skill directory; retain only runtime resources,
references, templates, dependency manifests, and attribution.

## External Workflow

Install and update Compound Engineering through Codex plugin or marketplace tooling outside this
repository. `install_dev_skills.py` manages only the local skills declared in `skills.json`; it does
not modify Codex marketplaces, plugin caches, or companion agent state.

Install standalone skills such as `last30days` directly from upstream. They are outside this
repository's bundle, sync manifest, and removal policy.

## Avoid

- Recreating old workstream queues or a heavyweight workflow runtime.
- Reintroducing Loom or Project Compass as active workflows.
- Keeping legacy machine ledgers as active authority.
- Treating engineering wiki memory as higher-priority instruction than current repo and user context.
- Treating external CE skills as files owned by this repository.

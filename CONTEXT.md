# Dev Skills Context

## Current Direction

This repository owns a lightweight personal Codex skill set:

- local utility skills for commits, Codex session recovery, and prose cleanup
- vendored Matt Pocock skills for small composable engineering and productivity workflows
- vendored `last30days` for recency-oriented social and web research
- scripts that install, check, and update the external Compound Engineering plugin

Compound Engineering is the preferred engineering workflow. Keep it as a plugin, not as vendored
`ce-*` skill bodies.

## Retained Local Skills

- `commit-work`
- `codex-session-recovery`
- `codex-subagent-cleanup`
- `humanizer`

## Vendored Upstream Skills

Matt Pocock's current default set is vendored with source attribution:

- engineering: `diagnose`, `grill-with-docs`, `improve-codebase-architecture`, `prototype`,
  `setup-matt-pocock-skills`, `tdd`, `to-issues`, `to-prd`, `triage`, `zoom-out`
- productivity: `caveman`, `grill-me`, `handoff`, `teach`, `write-a-skill`

## Vendored Research Skills

- `last30days` from `mvanhorn/last30days-skill`

This skill is intentionally larger than the rest of the repository because it vendors its upstream
research engine scripts and assets. Keep it source-attributed and update it via
`sync_upstream_skills.py` rather than hand-editing the copied files.

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
- Treating external CE skills as files owned by this repository.

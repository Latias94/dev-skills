# Dev Skills

Reusable Codex skills for large Rust projects.

This repo follows the small-skill style from
[`mattpocock/skills`](https://github.com/mattpocock/skills), but it is Codex-focused and does not
include Claude plugin packaging.

## Recommended Upstream Skills

Install these from `mattpocock/skills` first:

- `grill-with-docs`
- `tdd`
- `diagnose`
- `zoom-out`
- `handoff`
- `improve-codebase-architecture`
- `to-prd`
- `to-issues`
- `triage`

This repo does not vendor those skills. It composes with them.

## Skills

### Engineering

- [`dev-flow`](./skills/engineering/dev-flow/SKILL.md) — choose the right skill and route a Rust
  development session through bootstrap, clarification, planning, execution, validation, and
  closeout.
- [`bootstrap-rust-project`](./skills/engineering/bootstrap-rust-project/SKILL.md) — initialize
  large Rust project workflow docs for Codex, ADRs, and workstreams.
- [`rust-workstream`](./skills/engineering/rust-workstream/SKILL.md) — run a large Rust workstream:
  clarify requirements, create a task ledger, coordinate workers, and close with evidence.

## Workflow Diagram

See [`docs/workflow.md`](./docs/workflow.md) for the skill routing, artifact authority, and
multi-agent execution diagrams.

See [`docs/design-principles.md`](./docs/design-principles.md) for how this repo borrows from
Trellis and `mattpocock/skills` without duplicating their responsibilities.

See [`docs/install.md`](./docs/install.md) for install sets and the PowerShell/Python installers.
See [`docs/usage.md`](./docs/usage.md) for how users should call the skills and when to use Codex
goals.

## Install Locally

Default install copies local required skills and the minimal upstream dependencies:

```powershell
python .\scripts\install_dev_skills.py
```

PowerShell equivalent:

```powershell
.\scripts\install-dev-skills.ps1
```

Restart Codex after installing or updating skills.

## Workflow Shape

Use upstream skills for the sharp single-purpose moves:

- `grill-with-docs` to clarify requirements and challenge terminology.
- `tdd` and `diagnose` for execution feedback loops.
- `handoff` for compact session transfer.

Use local skills for the project-level workflow:

- `dev-flow` decides which skill and workflow phase should handle the request.
- `bootstrap-rust-project` creates reusable project docs and conventions.
- `rust-workstream` decides when to open a workstream, how to split tasks, and how to coordinate
  multiple agents without creating duplicate sources of truth.

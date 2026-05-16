# Dev Skills

Reusable Codex skills for large Rust projects.

Dev Skills gives you a Trellis-like development experience without replacing your project docs:
start from one entrypoint, clarify requirements, open an ADR/workstream-backed execution lane, split
vertical tasks, run implementation or diagnosis loops, and leave a traceable record for future
sessions and agents.

## Experience

Most users start with one prompt:

```text
Use $dev-flow to plan and execute this Rust change.
```

`$dev-flow` acts as an orchestrator. It should route the session to the right specialized skill:

```text
dev-flow -> grill-with-docs -> rust-workstream -> tdd/diagnose -> handoff/closeout
```

Users should not need to remember every skill. They can start with `$dev-flow`; the skill decides
when to delegate to requirement grilling, workstream planning, TDD, diagnosis, issue export, or
handoff.

## Development Model

The workflow is built for large projects where chat history is not a reliable source of truth.

```text
ADR -> workstream -> task ledger -> journal/handoff -> chat
```

- **ADR** records long-term architecture contracts and hard-to-change decisions.
- **Workstream** records a durable engineering lane: design, milestones, evidence, gates, and
  closeout.
- **Task ledger** records multi-agent slices in `TODO.md` with owner, scope, dependencies,
  validation, and handoff notes.
- **Journal / handoff** records session state for continuity, but never outranks ADRs or
  workstream docs.

This makes each task traceable: why it exists, which contract it follows, which worker owned it,
which files changed, and which gates prove it.

## Skills

### Local Skills

- [`dev-flow`](./skills/engineering/dev-flow/SKILL.md) — orchestrates the whole development flow
  and delegates to the right skill.
- [`bootstrap-rust-project`](./skills/engineering/bootstrap-rust-project/SKILL.md) — initializes a
  Rust repo with Codex-friendly workflow docs, workstream conventions, and multi-agent guardrails.
- [`rust-workstream`](./skills/engineering/rust-workstream/SKILL.md) — creates/reuses workstreams,
  writes task ledgers, coordinates workers, and records evidence.

### Upstream Skills Used By This Workflow

These come from [`mattpocock/skills`](https://github.com/mattpocock/skills):

- `grill-with-docs` — clarify requirements against project language and docs.
- `tdd` — implement bounded feature slices with red-green-refactor.
- `diagnose` — debug bugs, test failures, flakes, and performance regressions.
- `handoff` — compact the current session for another agent.
- `zoom-out` — understand unfamiliar code in system context.
- `improve-codebase-architecture` — find architecture and refactor opportunities.
- `to-prd`, `to-issues`, `triage` — optional tracker/spec workflow.

Dev Skills does not vendor those upstream skills. It composes with them.

## Copyable Prompts

Start a normal session:

```text
Use $dev-flow to plan and execute this Rust change. Route to the right skill as needed.
```

Initialize a repo:

```text
Use $dev-flow to initialize this Rust repo for the dev-skills workflow.
```

Clarify a risky feature:

```text
Use $dev-flow for this feature. If the requirements or architecture boundaries are unclear, delegate to $grill-with-docs before planning.
```

Open a workstream:

```text
Use $rust-workstream to create a workstream for this refactor, write DESIGN/TODO/MILESTONES/EVIDENCE_AND_GATES/WORKSTREAM.json, and split vertical tasks.
```

Execute one task:

```text
Use $tdd to implement task ABC-020 from docs/workstreams/<slug>/TODO.md. Stay within the assigned scope and update evidence.
```

Debug a failing task:

```text
Use $diagnose to reproduce and fix the failure for task ABC-020, then record the regression gate.
```

Coordinate multiple agents:

```text
Use $rust-workstream to split this workstream into parallel-safe worker tasks with owners, file scopes, dependencies, and validation commands.
```

Use Codex goals:

```text
Set task ABC-020 from docs/workstreams/<slug>/TODO.md as the current Codex goal. Complete it only after validation passes and the task ledger is updated.
```

## Install

Default install copies local required skills and the minimal upstream dependencies:

```powershell
python .\scripts\install_dev_skills.py
```

PowerShell equivalent:

```powershell
.\scripts\install-dev-skills.ps1
```

Optional recommended upstream skills:

```powershell
python .\scripts\install_dev_skills.py --include-recommended
```

Restart Codex after installing or updating skills.

See [`docs/install.md`](./docs/install.md) for install sets and options.

## Diagrams And Details

- [`docs/workflow.md`](./docs/workflow.md) — skill routing, artifact authority, and multi-agent
  execution diagrams.
- [`docs/usage.md`](./docs/usage.md) — user calls, Codex goals, and multi-agent usage.
- [`docs/design-principles.md`](./docs/design-principles.md) — how this borrows from Trellis and
  `mattpocock/skills`.

## Influences

- [`mattpocock/skills`](https://github.com/mattpocock/skills): small, composable skills with clear
  trigger descriptions, concise bodies, references, and assets.
- [`Trellis`](https://github.com/mindfold-ai/Trellis): task-centered development experience,
  planner/worker/reviewer roles, session continuity, and explicit execution flow.

Dev Skills adopts those ideas while keeping project-owned ADRs and workstreams as the authority.

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
dev-flow -> grill-with-docs -> open-workstream -> run-workstream-task -> close-workstream/handoff
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

## Failure Modes This Fixes

Dev Skills is a set of small workflow skills, not a full project-management framework.

- **Agent starts coding too early** -> `$dev-flow` routes risky requirements to
  `$grill-with-docs`.
- **Big Rust changes lose the thread** -> `$open-workstream` creates durable docs and a task
  ledger.
- **New sessions do not know what happened** -> `$resume-workstream` reads `WORKSTREAM.json`,
  `TODO.md`, `HANDOFF.md`, journal, and git state.
- **Multiple agents collide** -> `TODO.md` records owner, scope, dependencies, and validation per
  task.
- **A worker tries to do everything** -> `$run-workstream-task` owns exactly one task.
- **The lane never closes** -> `$close-workstream` finalizes evidence, gates, status, and follow-ons.

## Skills

### Local Skills

- [`dev-flow`](./skills/engineering/dev-flow/SKILL.md) — orchestrates the whole development flow
  and delegates to the right skill.
- [`setup-rust-workstreams`](./skills/engineering/setup-rust-workstreams/SKILL.md) — initializes a
  Rust repo with Codex-friendly workflow docs, workstream conventions, and multi-agent guardrails.
- [`open-workstream`](./skills/engineering/open-workstream/SKILL.md) — creates or reuses a durable
  lane and writes the workstream artifact set.
- [`run-workstream-task`](./skills/engineering/run-workstream-task/SKILL.md) — executes one task
  from `TODO.md` and delegates to `tdd` or `diagnose`.
- [`resume-workstream`](./skills/engineering/resume-workstream/SKILL.md) — reconstructs state from
  `WORKSTREAM.json`, `TODO.md`, `HANDOFF.md`, journal, and git state.
- [`close-workstream`](./skills/engineering/close-workstream/SKILL.md) — finalizes evidence, gates,
  status, and follow-ons.

### Upstream Skills Used By This Workflow

These come from [`mattpocock/skills`](https://github.com/mattpocock/skills):

- `grill-with-docs` — clarify requirements against project language and docs.
- `tdd` — implement bounded feature slices with red-green-refactor.
- `diagnose` — debug bugs, test failures, flakes, and performance regressions.
- `handoff` — compact the current session for another agent.
- `zoom-out` — understand unfamiliar code in system context.
- `improve-codebase-architecture` — find architecture and refactor opportunities.
- `to-prd`, `to-issues`, `triage`, `setup-matt-pocock-skills` — optional tracker/spec workflow.

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
Use $open-workstream to create a workstream for this refactor, write DESIGN/TODO/MILESTONES/EVIDENCE_AND_GATES/WORKSTREAM.json, and split vertical tasks.
```

Execute one task:

```text
Use $run-workstream-task to execute task ABC-020 from docs/workstreams/<slug>/TODO.md. Delegate to $tdd or $diagnose as needed, stay within scope, and update evidence.
```

Debug a failing task:

```text
Use $run-workstream-task to diagnose task ABC-020, reproduce the failure, fix it, and record the regression gate.
```

Coordinate multiple agents:

```text
Use $open-workstream to split this workstream into parallel-safe worker tasks with owners, file scopes, dependencies, and validation commands.
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

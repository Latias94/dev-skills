# Dev Skills

Reusable Codex skills for large Rust projects.

Dev Skills gives you a Trellis-like development experience without replacing your project docs:
start from one entrypoint, clarify requirements, open an ADR/workstream-backed execution lane, split
vertical tasks, run implementation or diagnosis loops, and leave a traceable record for future
sessions and agents.

## Experience

Most users start with one prompt:

```text
Use $dev-flow to work on this Rust project.
```

`$dev-flow` acts as an orchestrator. Users describe intent; the skill decides whether to initialize
docs, clarify requirements, open or resume a workstream, run a bounded task, diagnose a failure,
review architecture, or prepare a handoff.

Internal routing looks like this:

```text
dev-flow -> grill-with-docs -> open-workstream -> coordinate-workstream -> run-workstream-task -> close-workstream/handoff
```

Users should not need to manually call `open-workstream`, `resume-workstream`,
`run-workstream-task`, or `close-workstream` during ordinary development. Those are workflow actions
that `$dev-flow` should invoke when the project state calls for them.

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
- [`coordinate-workstream`](./skills/engineering/coordinate-workstream/SKILL.md) — coordinates
  planner, worker, reviewer, and docs terminals for one active workstream.
- [`run-workstream-task`](./skills/engineering/run-workstream-task/SKILL.md) — executes one task
  from `TODO.md` and delegates to `tdd` or `diagnose`.
- [`resume-workstream`](./skills/engineering/resume-workstream/SKILL.md) — reconstructs state from
  `WORKSTREAM.json`, `TODO.md`, `HANDOFF.md`, journal, and git state.
- [`close-workstream`](./skills/engineering/close-workstream/SKILL.md) — finalizes evidence, gates,
  status, and follow-ons.

### Upstream Skills Used By This Workflow

These come from [`mattpocock/skills`](https://github.com/mattpocock/skills):

- **Required by the flow**: `grill-with-docs`, `tdd`, `diagnose`, `handoff`.
- **Recommended for large Rust projects**: `zoom-out`, `improve-codebase-architecture`, `prototype`.
- **Direct, situational calls**: `setup-matt-pocock-skills`, `to-prd`, `to-issues`, `triage`,
  `write-a-skill`, `grill-me`, `caveman`.

Dev Skills does not vendor those upstream skills. It composes with them.

## User-Facing Prompts

Most daily work should start with intent, not an internal workflow step.

Start or continue normal development:

```text
Use $dev-flow to continue this Rust project.
```

Initialize a repo:

```text
Use $dev-flow to initialize this Rust repo for the dev-skills workflow.
```

Plan a large feature:

```text
Use $dev-flow to plan this feature. Clarify requirements first if needed, then create or reuse the right workstream and split executable tasks.
```

Execute a known task:

```text
Use $dev-flow to execute task ABC-020 from docs/workstreams/<slug>/TODO.md.
```

Debug a failure:

```text
Use $dev-flow to debug this failing test and record the regression evidence in the active workstream.
```

Prepare a handoff:

```text
Use $dev-flow to prepare a handoff for the current workstream.
```

## When To Call Other Skills Directly

Some skills are explicit user actions. Call them directly when that is the thing you want done.

Recommended upstream skills for your kind of work:

```text
Use $zoom-out when you need a system-level explanation of unfamiliar code.
Use $improve-codebase-architecture when you want a structural review after some code exists.
Use $prototype when you want a throwaway experiment before choosing a design.
```

Configure Matt Pocock issue-tracker/domain-doc assumptions:

```text
Use $setup-matt-pocock-skills to configure AGENTS.md and docs/agents for this repo.
```

Stress-test an idea before it becomes project docs:

```text
Use $grill-me to challenge this project idea until the MVP, non-goals, and risks are precise.
```

Build a throwaway experiment:

```text
Use $prototype to test two possible execution-loop designs before we commit to the architecture.
```

Export to tracker artifacts:

```text
Use $to-prd to turn the clarified plan into a PRD, then $to-issues if it should become GitHub issues.
```

Create a new reusable workflow skill:

```text
Use $write-a-skill to create an emulator-trace-debug skill for trace divergence debugging.
```

Use Codex goals for one bounded task:

```text
Set task ABC-020 from docs/workstreams/<slug>/TODO.md as the current Codex goal. Complete it only after validation passes and the task ledger is updated.
```

## Example: Rust Emulator Project

Day 0, start from a new idea:

```text
Use $dev-flow to start a new Rust homebrew-first emulator/simulator project.
Initialize workflow docs if missing, clarify the MVP and legal/scope boundaries, propose the first architecture decisions, then open the first durable workstream.
Do not start broad implementation until the first validation gate is clear.
```

Early architecture experiment:

```text
Use $prototype to compare memory-bus and execution-trace designs for this emulator.
Keep it throwaway. Summarize what should become ADR material.
```

Normal workday:

```text
Use $dev-flow to continue the emulator project.
Read the active workstream state, pick the next safe task, execute it with tests, and update evidence.
```

Multi-agent planning:

```text
Use $dev-flow to prepare parallel work for the active emulator workstream.
Split tasks only when owners, file scopes, dependencies, and validation commands are clear.
```

Planner / PM terminal:

```text
Use $coordinate-workstream to coordinate the active emulator workstream across planner, worker,
reviewer, and next-version docs terminals.
```

Debugging:

```text
Use $dev-flow to diagnose the trace divergence in the active emulator task.
Build a deterministic repro, fix it, add a regression test, and update the evidence gate.
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

Recommended upstream skills:

```powershell
python .\scripts\install_dev_skills.py --include-recommended
```

Restart Codex after installing or updating skills.

See [`docs/install.md`](./docs/install.md) for install sets and options.

Validate local skill authoring rules:

```powershell
python .\scripts\validate_skills.py
```

## Diagrams And Details

- [`docs/workflow.md`](./docs/workflow.md) — skill routing, artifact authority, and multi-agent
  execution diagrams.
- [`docs/usage.md`](./docs/usage.md) — user calls, Codex goals, and multi-agent usage.
- [`docs/playbooks/multi-terminal-development.md`](./docs/playbooks/multi-terminal-development.md)
  — planner, worker, reviewer, and docs terminal prompts.
- [`docs/design-principles.md`](./docs/design-principles.md) — how this borrows from Trellis and
  `mattpocock/skills`.

## Influences

- [`mattpocock/skills`](https://github.com/mattpocock/skills): small, composable skills with clear
  trigger descriptions, concise bodies, references, and assets.
- [`Trellis`](https://github.com/mindfold-ai/Trellis): task-centered development experience,
  planner/worker/reviewer roles, session continuity, and explicit execution flow.

Dev Skills adopts those ideas while keeping project-owned ADRs and workstreams as the authority.

# Dev Skills

Reusable Codex skills for Rust projects, from small repos to large workspaces.

Chinese documentation: [README.zh-CN.md](./README.zh-CN.md)

Dev Skills gives you a Trellis-like development experience without replacing your project docs:
start from one entrypoint, clarify requirements, open an ADR/workstream-backed execution lane, split
vertical tasks, run implementation or diagnosis loops, review completed slices, verify with fresh
evidence, and leave a traceable record for future sessions and agents.

## Experience

Most users start with one prompt:

```text
Use $dev-flow to work on this Rust project.
```

If the repo is unfamiliar, has old workflow docs, or may or may not need multiple terminals, audit
the project scale first:

```text
Use $audit-project-scale on this Rust repo and choose the right dev-skills path.
```

For large projects, a terminal can also be assigned to one architecture lane:

```text
Use $run-architecture-lane for the storage lane.
```

`$dev-flow` acts as an orchestrator. Users describe intent; the skill decides whether to initialize
docs, clarify requirements, open or resume a workstream, run a bounded task, diagnose a failure,
review architecture, assign an architecture lane, or prepare a handoff.

Internal routing looks like this:

```text
audit-project-scale -> dev-flow -> grill-with-docs -> open-workstream/run-architecture-lane -> run-workstream-task -> review-workstream -> verify-rust-workstream -> close-workstream/handoff
```

Users should not need to manually call `open-workstream`, `resume-workstream`,
`run-workstream-task`, `review-workstream`, `verify-rust-workstream`, or `close-workstream` during
ordinary development. Those are workflow actions that `$dev-flow` should invoke when the project
state calls for them.

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

For large systems, an **architecture lane** can bind one terminal/worktree to a capability area such
as storage, transcode, playback, realtime, or admin. The terminal advances a queue of related
workstreams while keeping shared scopes explicit.

## Choosing Workflow Scale

Use the smallest workflow shape that protects the project.

| Repo situation | User-facing skill | Expected shape |
| --- | --- | --- |
| Small repo, one terminal, one bounded bug or feature | `$dev-flow` | Direct `tdd` / `diagnose`, maybe no workstream |
| Medium repo, multi-step feature or refactor | `$dev-flow` | One workstream with task ledger and evidence gates |
| Large repo with stable capability areas | `$audit-project-scale`, then `$run-architecture-lane` | Lane terminals per capability plus planner coordination |
| Multiple terminals already active | `$coordinate-workstream` | Planner integrates lane / worker / reviewer output |
| Old or unclear workstream/architecture docs | `$audit-project-scale` | Repair substrate before planning new work |

## Failure Modes This Fixes

Dev Skills is a set of small workflow skills, not a full project-management framework.

- **Unsure whether the repo needs lanes or just one task** -> `$audit-project-scale` classifies the
  repo and routes to the smallest fitting workflow.
- **Agent starts coding too early** -> `$dev-flow` routes risky requirements to
  `$grill-with-docs`.
- **Big Rust changes lose the thread** -> `$open-workstream` creates durable docs and a task
  ledger.
- **New sessions do not know what happened** -> `$resume-workstream` reads `WORKSTREAM.json`,
  `TODO.md`, `HANDOFF.md`, journal, and git state.
- **Multiple agents collide** -> `TODO.md` records owner, scope, dependencies, and validation per
  task.
- **Large architecture areas require too much terminal switching** -> `$run-architecture-lane`
  keeps one terminal focused on a capability across multiple workstreams.
- **A worker tries to do everything** -> `$run-workstream-task` owns exactly one task.
- **Worker output is accepted on trust** -> `$review-workstream` separates contract review from code
  quality review.
- **Completion claims rely on old output** -> `$verify-rust-workstream` requires fresh command
  evidence.
- **The lane never closes** -> `$close-workstream` finalizes evidence, gates, status, and follow-ons.

## Skills

### User-Facing Local Skills

- [`dev-flow`](./skills/engineering/dev-flow/SKILL.md) — orchestrates the whole development flow
  and delegates to the right skill.
- [`audit-project-scale`](./skills/engineering/audit-project-scale/SKILL.md) — audits repo size,
  existing docs, and multi-terminal readiness before choosing direct tasks, workstreams, or
  architecture lanes.
- [`run-architecture-lane`](./skills/engineering/run-architecture-lane/SKILL.md) — keeps one
  terminal focused on a large architecture area across a sequence of workstreams.
- [`coordinate-workstream`](./skills/engineering/coordinate-workstream/SKILL.md) — coordinates
  planner, lane, worker, reviewer, and docs terminals across workstreams or architecture lanes.
- [`codex-session-recovery`](./skills/engineering/codex-session-recovery/SKILL.md) — manually
  recovers continuity from Codex session JSONL files after context corruption, crashes, or
  encrypted-content failures.

Most users should learn only these. The remaining local skills are internal workflow steps that
`$dev-flow`, `$run-architecture-lane`, or `$coordinate-workstream` should invoke.

### Internal Local Workflow Skills

- [`setup-rust-workstreams`](./skills/engineering/setup-rust-workstreams/SKILL.md) — initializes a
  Rust repo with Codex-friendly workflow docs, workstream conventions, and multi-agent guardrails.
- [`fearless-refactor`](./skills/engineering/fearless-refactor/SKILL.md) — converts architecture
  review findings into a dev-flow-backed Rust refactoring lane.
- [`open-workstream`](./skills/engineering/open-workstream/SKILL.md) — creates or reuses a durable
  lane and writes the workstream artifact set.
- [`run-workstream-task`](./skills/engineering/run-workstream-task/SKILL.md) — executes one task
  from `TODO.md` and delegates to `tdd` or `diagnose`.
- [`review-workstream`](./skills/engineering/review-workstream/SKILL.md) — reviews task diffs and
  worker handoffs against workstream compliance and code quality.
- [`verify-rust-workstream`](./skills/engineering/verify-rust-workstream/SKILL.md) — runs fresh Rust
  validation gates before task, goal, or lane completion claims.
- [`resume-workstream`](./skills/engineering/resume-workstream/SKILL.md) — reconstructs state from
  `WORKSTREAM.json`, `TODO.md`, `HANDOFF.md`, journal, and git state.
- [`close-workstream`](./skills/engineering/close-workstream/SKILL.md) — finalizes evidence, gates,
  status, and follow-ons.
- [`changelog`](./skills/engineering/changelog/SKILL.md) — updates `CHANGELOG.md` from git history
  in Keep a Changelog style for SemVer projects.

### Misc Skills

Misc skills are useful with Codex but are not part of the default Rust engineering workflow. They
are not installed unless explicitly requested.

- [`humanizer`](./skills/misc/humanizer/SKILL.md) — removes signs of AI-generated writing from prose
  while preserving meaning, facts, terminology, and intended voice. Adapted from
  [`blader/humanizer`](https://github.com/blader/humanizer).

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

Audit an existing or uncertain repo:

```text
Use $audit-project-scale on this Rust repo. Decide whether it should use direct $dev-flow tasks,
normal workstreams, or architecture lanes with a planner terminal.
```

Plan a large feature:

```text
Use $dev-flow to plan this feature. Clarify requirements first if needed, then create or reuse the right workstream and split executable tasks.
```

Run a long-lived architecture terminal:

```text
Use $run-architecture-lane for the nako storage lane. Keep this terminal focused on storage/VFS workstreams and stop when shared database or server contracts need coordination.
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

Review and verify a completed task:

```text
Use $dev-flow to review and verify task ABC-020 before marking it complete.
```

Recover from a broken Codex session:

```text
Use $codex-session-recovery to recover continuation context from the latest Codex session.
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

Recover after a crash or `encrypted_content` failure:

```text
Use $codex-session-recovery to read this Codex session id and reconstruct the active goal, recent tool activity, compaction summary, and safe continuation plan: 019e2779-da60
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
Read the active workstream state, pick the next safe task, execute it with tests, review the result,
verify fresh gates, and update evidence.
```

Multi-agent planning:

```text
Use $dev-flow to prepare parallel work for the active emulator workstream.
Split tasks only when owners, file scopes, dependencies, and validation commands are clear.
```

Planner / PM terminal:

```text
Use $coordinate-workstream to inspect the emulator repo, identify active workstreams or architecture
lanes, and recommend planner, worker, reviewer, and next-version docs terminals.
```

Reviewer terminal:

```text
Use $review-workstream to review the completed emulator task against workstream compliance and code quality.
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

Recommended skills, including session recovery, changelog maintenance, and fearless refactoring:

```powershell
python .\scripts\install_dev_skills.py --include-recommended
```

Misc skills, such as writing helpers:

```powershell
python .\scripts\install_dev_skills.py --include-misc
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
- [`Superpowers`](https://github.com/obra/superpowers): hard gates for planning, review, fresh
  verification, and worker status discipline.

Dev Skills adopts those ideas while keeping project-owned ADRs and workstreams as the authority.

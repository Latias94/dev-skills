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

If the input is still a broad product ambition, shape the product architecture before opening
workstreams:

```text
Use $shape-product-architecture to turn this product goal into a bounded vision, MVP ladder,
capability map, architecture lanes, ADR candidates, and initial workstream priorities.
```

For large projects, a terminal can also be assigned to one architecture lane:

```text
Use $run-architecture-lane for the storage lane.
```

`$dev-flow` acts as an orchestrator. Users describe intent; the skill decides whether to initialize
docs, clarify requirements, open or resume a workstream, run a bounded task, diagnose a failure,
review architecture, assign an architecture lane, or prepare a handoff.

For large projects, users usually keep one upper architecture terminal open and talk directly with
lane terminals. The upper terminal periodically reviews progress and integration risk; lane
terminals keep deepening their own sub-architecture within approved boundaries.

Internal routing looks like this:

```text
audit-project-scale -> dev-flow -> grill-with-docs/shape-product-architecture/plan-engineering-program/plan-architecture-lane -> open-workstream/run-architecture-lane -> integrate-lane-results/review-workstream/verify-rust-workstream -> close-workstream/handoff
```

Users should not need to manually call `plan-architecture-lane`, `open-workstream`,
`resume-workstream`, `run-workstream-task`, `review-workstream`, `verify-rust-workstream`, or
`close-workstream` during ordinary development. Those are workflow actions that `$dev-flow`,
`$plan-engineering-program`, `$run-architecture-lane`, or `$integrate-lane-results` should invoke
when the project state calls for them.

When the next step is ambiguous, the agent should say the current phase, recommended route, why,
what it can do read-only now, which side effects need approval, and the exact prompt or artifact the
user should use next.

## Development Model

The workflow is built for large projects where chat history is not a reliable source of truth.

```text
product docs -> ADR -> workstream -> task ledger -> journal/handoff -> chat
```

- **Product docs** record product intent, reference-product pressure, MVP stages, client surfaces,
  non-goals, capability maps, and priority classes.
- **ADR** records long-term architecture contracts and hard-to-change decisions.
- **Workstream** records a durable engineering lane: design, milestones, evidence, gates, and
  closeout.
- **Task ledger** records multi-agent slices in `TODO.md` with owner, scope, dependencies,
  validation, and handoff notes.
- **Journal / handoff** records session state for continuity, but never outranks ADRs or
  workstream docs.

This makes each task traceable: why it exists, which contract it follows, which worker owned it,
which files changed, and which gates prove it.

The upper architecture planner owns lane maps, campaign queues, shared-scope sequencing, and global
integration order. Lane terminals own one capability area and may propose the next same-lane medium
goal when their campaign finishes. Before creating workstreams or bundles,
`$plan-engineering-program` and `$plan-architecture-lane` choose planning depth: light planning when
docs match the code, code-aware planning when task boundaries need code evidence, or an architecture
review pass when lane seams or docs/code alignment are unclear.

For large systems, an **architecture lane** can bind one terminal/worktree to a capability area such
as storage, transcode, playback, realtime, or admin. The terminal advances a queue of related
workstreams while keeping shared scopes explicit.

For multi-worktree work, prefer one stable worktree per architecture lane, not one worktree per
workstream. The upper planner proposes terminal/worktree layout, branch names, creation commands,
and prompts; after user approval it may create the worktrees or hand the commands to the user. Lane
terminals recommend the next same-lane medium goal after each campaign, but the upper planner owns
cross-lane sequencing.

For long-running terminals, the upper planner should prepare a **lane goal bundle** before execution: one
lane, one stable worktree, one active workstream or short same-lane queue, one to three ready tasks,
owned/shared scopes, validation commands, a context manifest, and stop conditions. Codex goals fit
that bundle, one bounded task, or an approved lane campaign; they should not represent an
entire architecture lane.
When a bundle, campaign, or task is ready for longer autonomous work, planner or lane output should
include the exact Codex goal to set and explicitly ask whether this terminal should set it. If the
user already approved goal setup in the current conversation, set the bounded goal directly so lane
terminals can execute until done, blocked, or a stop condition appears.

When a lane should keep deepening over many sessions, keep that ambition in architecture docs or a
lane roadmap: current state, target maturity, capability gaps, active/draft/deferred workstreams,
validation ladder, shared scopes, and next bundles. If the queue gets too small,
`$plan-engineering-program` should refresh the lane backlog with source coverage, scoped
`$plan-architecture-lane`, and `$improve-codebase-architecture` when docs/code alignment is unclear.
It should proactively mine same-lane deepening candidates instead of only consuming existing TODOs.
If enough ordered bundles are ready, the upper planner can approve a lane campaign so the goal runs
through several bundles with auto-advance gates and checkpoints before asking for more input. When
work is not parallelizable but can proceed as an ordered lane sequence, use one serial lane campaign
on a stable worktree instead of repeated one-task prompts.
Campaigns should carry an explicit side-effect policy: `manual`, `auto-commit-sync`, or
`auto-commit-sync-merge`. Use it to commit at accepted bundle boundaries, sync main into a lane
worktree, or merge an accepted lane slice back to main after fresh
gates. The agent still stops for conflicts, failed gates, unrelated dirty files, ADR/schema/public
contract changes, related-repo decisions, or unapproved pushes.

## Guiding Method

The workflow combines practical software-engineering methods:

- **Domain-Driven Design** for shared language, ADRs, and capability boundaries.
- **Team Topologies** for one terminal/worktree per stream-aligned architecture lane.
- **Shape Up** for medium-sized campaigns instead of tiny prompt churn or unbounded goals.
- **Mikado Method** for dependency-aware refactoring before shared contracts move.
- **Theory of Constraints** for critical-path scheduling instead of maximizing terminal count.
- **XP/TDD and Continuous Delivery** for fast feedback, review, verification, and frequent safe
  integration.

The operating principle is intent compression: durable lane docs, campaigns, ADRs, and gates should
let a short prompt communicate accurate intent. Treat user attention as the scarcest token: agents
should spend read-only investigation time before asking for direction, and ask only for real
product/architecture decisions or side effects not already covered by the approved campaign policy.

## Choosing Workflow Scale

Use the smallest workflow shape that protects the project.

| Repo situation | User-facing skill | Expected shape |
| --- | --- | --- |
| Broad product goal, unclear MVP, or reference-product ambition | `$shape-product-architecture` | Product vision, MVP ladder, capability map, lanes, and ADR candidates |
| Small repo, one terminal, one bounded bug or feature | `$dev-flow` | Direct `tdd` / `diagnose`, maybe no workstream |
| Medium repo, multi-step feature or refactor | `$dev-flow` | One workstream with task ledger and evidence gates |
| Large repo with stable capability areas | `$audit-project-scale`, then `$plan-engineering-program` and `$run-architecture-lane` | Stable lane worktrees plus approved campaigns |
| Multiple terminals already active | `$plan-engineering-program` / `$integrate-lane-results` | Upper planning for next campaigns; integration for completed output |
| Old or unclear workstream/architecture docs | `$audit-project-scale` | Repair substrate before planning new work |

## Failure Modes This Fixes

Dev Skills is a set of small workflow skills, not a full project-management framework.

- **Unsure whether the repo needs lanes or just one task** -> `$audit-project-scale` classifies the
  repo and routes to the smallest fitting workflow.
- **Big product ambition turns into shallow TODOs** -> `$shape-product-architecture` shapes the
  product intent, MVP ladder, capability map, and ADR candidates before execution planning.
- **Agent starts coding too early** -> `$dev-flow` routes risky requirements to
  `$grill-with-docs`.
- **Big Rust changes lose the thread** -> `$open-workstream` creates durable docs and a task
  ledger.
- **New sessions do not know what happened** -> `$resume-workstream` reads `WORKSTREAM.json`,
  `TODO.md`, `HANDOFF.md`, journal, and git state.
- **Multiple agents collide** -> `TODO.md` records owner, scope, dependencies, and validation per
  task.
- **A worker finishes and nobody knows the next step** -> `$integrate-lane-results` inspects the
  worktree result and returns review/verify, merge, or next-bundle action.
- **Agents reread too much or miss key context** -> `CONTEXT.jsonl` points terminals at the ADRs,
  architecture docs, evidence, and research they need before editing or reviewing.
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
- [`shape-product-architecture`](./skills/engineering/shape-product-architecture/SKILL.md) — turns a
  broad product ambition into product docs, MVP stages, capability maps, lane priorities, and ADR
  candidates.
- [`run-architecture-lane`](./skills/engineering/run-architecture-lane/SKILL.md) — keeps one
  terminal focused on a large architecture area across a sequence of workstreams.
- [`plan-engineering-program`](./skills/engineering/plan-engineering-program/SKILL.md) — plans the
  upper engineering program, lane maps, campaigns, worktrees, and macro sequencing.
- [`integrate-lane-results`](./skills/engineering/integrate-lane-results/SKILL.md) — inspects
  completed lane/worktree output and routes review, verification, fixes, merge, and sync.
- [`codex-session-recovery`](./skills/engineering/codex-session-recovery/SKILL.md) — manually
  recovers continuity from Codex session JSONL files after context corruption, crashes, or
  encrypted-content failures.

Most users should learn only these. The remaining local skills are internal workflow steps that
`$dev-flow`, `$run-architecture-lane`, `$plan-engineering-program`, or `$integrate-lane-results`
should invoke.

### Internal Local Workflow Skills

- [`setup-rust-workstreams`](./skills/engineering/setup-rust-workstreams/SKILL.md) — initializes a
  Rust repo with Codex-friendly workflow docs, workstream conventions, and multi-agent guardrails.
- [`fearless-refactor`](./skills/engineering/fearless-refactor/SKILL.md) — converts architecture
  review findings into a dev-flow-backed Rust refactoring lane.
- [`open-workstream`](./skills/engineering/open-workstream/SKILL.md) — creates or reuses a durable
  lane and writes the workstream artifact set.
- [`plan-architecture-lane`](./skills/engineering/plan-architecture-lane/SKILL.md) — turns a
  selected architecture direction into a workstream, worktree, and lane bundle plan.
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
- [`commit-work`](./skills/engineering/commit-work/SKILL.md) — creates safe, focused Conventional
  Commits from inspected and intentionally staged changes.

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

Dev Skills does not vendor those upstream skills. It composes with them: planner skills use
`zoom-out` and `improve-codebase-architecture` for read-only discovery, execution skills route to
`tdd` or `diagnose`, and documentation/continuity routes to `grill-with-docs` and `handoff`.

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
normal workstreams, or architecture lanes with an upper architecture terminal.
```

Plan a large feature:

```text
Use $dev-flow to plan this feature. Clarify requirements first if needed, then create or reuse the right workstream and split executable tasks.
```

Shape a product architecture:

```text
Use $shape-product-architecture to turn this product goal into a bounded vision, MVP ladder,
capability map, architecture lanes, ADR candidates, and initial workstream priorities.
```

Run a long-lived architecture terminal:

```text
Use $run-architecture-lane for the nako storage lane.
Use the approved lane bundle or lane campaign as the maximum autonomous scope.
Keep this terminal focused on storage/VFS workstreams and stop when shared database or server contracts need coordination.
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

Use a Codex goal for an approved lane bundle:

```text
Set the current Codex goal to complete lane bundle storage-20260530-01 from planner state.
Stay inside the bundle scope, stop on shared-scope changes or missing context, and report back for integration before continuing.
```

Use a Codex goal for an approved lane campaign:

```text
Set the current Codex goal to execute lane campaign storage-20260531-01 from planner state.
Auto-advance through the listed bundles only when each gate passes; stop on shared scopes, ADR/schema/contract changes, failed gates, missing context, or unapproved side effects.
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

Upper architecture terminal:

```text
Use $plan-engineering-program to inspect the emulator repo, identify active workstreams or architecture
lanes, and recommend upper-planner, lane, worker, reviewer, and next-version docs terminals.
Start with Program Action Mode, Now, and Why.
Plan lane goal bundles, or a deeper lane campaign when requirements, docs, and gates are clear.
List three to five candidate directions when evidence supports them, but activate at most three
lane/worker terminals by default. Use one planner/recon terminal or one serial campaign when lane
maps or module boundaries are unclear.
Include WIP count, assignment go/no-go, autonomy horizon, and integration bottleneck risk.
When the active queue is thin, proactively inspect code/docs and propose same-lane deepening
candidates instead of waiting for the user to ask.
After clearing blockers, repairing substrate, reconciling queues, or closing workstreams, return to
the planning question before implementation: can we parallelize now, what remains blocked, and what
terminal or serial campaign should run next?
After assigning terminals, continue with read-only architecture reconnaissance if there is no
integration/review work pending.
Use the program mode that fits the state: DISCOVERY, SHAPE, PLAN, ASSIGN, RECON, or DECISION.
When tasks are dependency-ordered and not parallelizable, prefer one serial lane campaign over
multiple blocked terminals or repeated copy/paste prompts.
For active or stale worktrees, use the result-intake helper before asking the user to paste chat.
Prefer one stable worktree per architecture lane. Do not create worktrees or branches until the user
approves the proposed layout, commands, terminal prompts, and any side effects.
Write the exact Codex goal to set for each approved task, bundle, or campaign.
```

Result integration:

```text
Use $integrate-lane-results to inspect the completed lane worktree, classify the result, route
review/verify, and propose fix, commit, merge, sync, or next-campaign actions.
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

Recommended skills, including session recovery, changelog maintenance, commit creation, and fearless
refactoring:

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
- [`docs/evals/large-rust-workflow.md`](./docs/evals/large-rust-workflow.md) — behavior eval
  prompts for product shaping, planner campaigns, lane execution, and integration intake.
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

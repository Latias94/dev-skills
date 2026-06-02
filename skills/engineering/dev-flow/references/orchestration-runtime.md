# Orchestration Runtime Model

Use this as the canonical control model for large multi-terminal development. Skills explain what
to do; runtime artifacts and scripts make the plan inspectable and repeatable.

## Layer Split

- Skills hold routing rules, role contracts, and decision policy.
- Repo artifacts hold durable truth: product docs, ADRs, architecture docs, workstreams, tasks,
  campaigns, gates, and handoffs.
- Local runtime state holds machine-specific facts: worktree paths, branch heads, active terminal
  roles, session pointers, and approved side-effect scope.
- Scripts inspect and validate state. They do not make architecture decisions.

Do not put long-running orchestration state only in chat. Chat and session tails are recovery hints.
Use `artifact-contracts.md` to decide where durable state belongs.

## Program State Machine

- `DISCOVERY`: gather read-only repo, docs, git, and worktree evidence.
- `SHAPE`: product, MVP, capability, or ADR direction is not ready for execution planning.
- `PLAN`: lane maps, workstreams, tasks, campaigns, or gates need design.
- `ASSIGN`: a task, bundle, or campaign is ready for a terminal.
- `EXECUTE`: a lane or worker terminal is running approved scope.
- `INTAKE`: completed output is reconstructed from git, docs, and session tails.
- `REVIEW`: contract and code-quality review is running.
- `VERIFY`: fresh gates are running or being recorded.
- `INTEGRATE`: accepted output is committed, synced, merged, or sequenced.
- `RECON`: planner does read-only next-wave discovery while execution continues.
- `DECISION`: user input is required for product, ADR, side-effect, cross-repo, or risk tradeoff.

Never jump from `EXECUTE` to a new `ASSIGN`. Intake, review, and fresh verification come first.

## Operating Modes

The planner and orchestrator should explicitly distinguish two read-only modes before assignment:

- `READINESS`: determine whether a task, bundle, or campaign is assignable now.
- `AUDIT`: inspect historical artifact quality, closeout hygiene, or evidence drift without blocking
  current assignment unless the drift touches the active queue.

Use `READINESS` when the user asks:

- what can run next,
- whether any lane is assignable,
- which task should be delegated,
- whether a campaign is ready,
- or to resume active work.

Use `AUDIT` when the user asks:

- whether old workstreams are well-formed,
- whether closeouts are consistent,
- whether evidence is complete,
- whether the workflow itself is healthy,
- or to evaluate the repo/process rather than assign execution.

Do not turn historical audit findings into assignment blockers unless they affect:

- the active workstream,
- the active lane queue,
- shared scope safety,
- current validation trust,
- or current machine-readable state required for execution.

In large repos, report both:

- `Mode: READINESS | AUDIT`
- `Implementation Horizon: <N>`

`Implementation Horizon` counts only ready active work units. Historical drift may lower confidence
or trigger follow-on cleanup, but it does not by itself set the horizon to zero.

## Plan, Fan Out, Verify, Converge

1. `Plan`: choose the smallest safe scale, source coverage, owned/shared scopes, validation gates,
   stop conditions, and side-effect policy.
2. `Fan out`: assign only disjoint terminal/worktree scopes, or use explorer sidecars for bounded
   read-only questions. Shared scopes stay serialized.
3. `Verify`: route results through `review-workstream` and `verify-rust-workstream`. Use adversarial
   or independent review when findings depend on interpretation.
4. `Converge`: update evidence, task state, campaign checkpoints, planner state, and lane roadmap
   before assigning more implementation.

Parallelism is useful only when convergence is cheaper than serial work.
Use `gate-taxonomy.md` for pre-flight, revision, escalation, and abort gates.
Use `codex-subagent-dispatch.md` when native Codex subagent tools are available.

## Machine-Readable Artifacts

Use these together:

- `TODO.md`: human task ledger and rationale.
- `TASKS.jsonl`: machine-readable task state. Each task has ID, status, owner, deps, scope,
  validation, context, evidence, and handoff status.
- `CAMPAIGNS.jsonl`: approved or draft medium autonomous units with ordered tasks or bundles,
  auto-advance rules, checkpoints, gates, stop conditions, and side-effect policy.
- `WORKSTREAM.json`: workstream summary, lane binding, current task, authoritative docs, and
  context manifest path.
- `EVIDENCE_AND_GATES.md`: proof claims and fresh gate results.
- `.codex/planner-state.local.json`: local runtime pointers only. Do not commit personal paths.

Markdown and JSONL must agree. If they disagree, stop in `PLAN` or `INTAKE` and repair the drift
before assigning more implementation.
The producer, consumer, and lifecycle contract for each artifact lives in `artifact-contracts.md`.

## Derived Runtime Bridge

Large-repo orchestration still needs a per-turn bridge between durable artifacts and the next prompt.
That bridge must stay derived, compact, and disposable.

Use:

- `skills/engineering/plan-engineering-program/scripts/planner_breadcrumb.py --format prompt`

The output is a prompt-ready `<planner-runtime>` block containing:

- current phase,
- operating mode,
- implementation horizon,
- active workstream/task/campaign,
- readiness blockers,
- required context,
- and the next planner move.

Rules:

- treat the block as runtime guidance, never as authoritative state,
- regenerate it from repo artifacts instead of editing it by hand,
- prepend it to planner, integrator, lane-intake, or readiness-audit prompts when the active queue
  is not obvious from the immediate local context,
- do not use it to bypass ADRs, architecture docs, workstream ledgers, or evidence gates.

This is the dev-skills answer to Trellis-style runtime injection: derive the control hint from
repo-owned artifacts instead of centralizing truth into a workflow control file.

## Assignment Gate

Assign implementation only when all are true:

- lane or temporary ownership boundary is clear,
- task or campaign state is machine-readable,
- context manifest exists and points to required docs,
- owned and shared scopes are explicit,
- validation is runnable,
- side-effect policy is stated,
- stop conditions are stated,
- dirty worktrees and unrelated changes are classified.

If any item is missing, report `Implementation Horizon: 0` and continue with `DISCOVERY`, `PLAN`,
or read-only `RECON`.
Use `worktree-safety.md` for branch/path/cwd checks before execution or integration.

Historical quality findings belong in `AUDIT`, not in the assignment gate, unless they invalidate
the active queue's authority or readiness.

## Goal Rule

Codex goals may execute:

- one bounded task,
- one approved lane goal bundle,
- one approved lane campaign.

Do not use a goal for an entire workstream, architecture lane, or vague maturity target. Durable
ambition belongs in architecture docs and lane backlogs; the goal references the next approved
runtime unit.

## Side-Effect Policy

Every campaign states exactly one policy. Use `side-effect-policy.md` for the full execution gate:

- `manual`: ask before commit, sync, merge, worktree creation, related-repo change, or push.
- `auto-commit`: commit accepted slices after review, fresh gates, and clean scope checks.
- `auto-commit-sync`: commit accepted slices after review and fresh gates, then sync main when clean.
- `auto-commit-sync-merge`: also merge accepted slices after listed post-merge gates pass.

Stop before conflicts, failed gates, unrelated dirty files, ADR/schema/public contract changes,
related-repo decisions, protected branch issues, or unapproved pushes.

## Script Contract

Status and validation scripts are read-only by default. A script may report:

- state summary,
- missing artifacts,
- task/campaign/docs drift,
- unsafe assignment blockers,
- prompts or goals to copy.

Scripts should not create branches, edit docs, commit, merge, or push unless a future explicit
side-effect command is added and approved by the user.

## Output Contract

Worker, lane, review, verify, and integration terminals return parseable markers from
`agent-contracts.md`. A plain prose `DONE` is not accepted completion.

## Context Rule

Use `context-budget.md` when the required reading list becomes large. Load durable contracts first,
then targeted evidence and code. Session tails are recovery hints, not primary state.

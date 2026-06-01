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

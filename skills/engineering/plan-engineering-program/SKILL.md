---
name: plan-engineering-program
description: >
  Plans and replans large Rust engineering programs across architecture lanes. Use when a project
  needs an upper architecture planner, lane roadmap/backlog/campaign design, multi-worktree
  terminal layout, proactive architecture reconnaissance, lane autonomy policy, or a decision about
  which sub-architecture terminals should keep working next.
---

# Plan Engineering Program

Use this from the upper architecture / commander terminal. This skill plans the program; it does
not implement lane work or accept worker `DONE` reports. Use `integrate-lane-results` for result
intake, review, verify, merge, and sync.

## Purpose

Make Codex understand the intent with fewer prompts by turning broad ambition into durable repo
artifacts: architecture lanes, lane roadmaps, campaigns, workstreams, ADRs, context manifests, and
validation gates. The user should be able to chat naturally with lane terminals while this terminal
keeps macro architecture control. Treat user attention as the scarcest token: spend agent time on
read-only investigation before asking the user to decide.

## Read First

- `CONTEXT.md`, `AGENTS.md`, and relevant ADRs
- `docs/architecture/LANES.md`, lane docs, and lane roadmaps/backlogs
- active `docs/workstreams/*/WORKSTREAM.json`, `TODO.md`, `EVIDENCE_AND_GATES.md`, `HANDOFF.md`
- git status, `git worktree list`, active branches, and related repo status
- relevant crates/modules/tests when lane boundaries or readiness are uncertain

Use `scripts/workstream_inventory.py <repo>` or `scripts/workstream_inventory.py --root <repo>`
when the repo has many workstreams and you need a fast status/lane inventory before planning.

Read references as needed: `methodology.md`, `matt-skill-leverage.md`, `program-artifacts.md`,
`campaign-planning.md`, `production-control.md`, `../dev-flow/references/planner-state.md`,
`../dev-flow/references/multi-agent-flow.md`, `../dev-flow/references/source-coverage-audit.md`,
and `../dev-flow/references/documentation-authority.md`.

## Process

1. Classify scale: direct task, workstream, lane, or full engineering program.
2. Reconcile authority: compare `LANES.md`, `WORKSTREAM.json`, TODO ledgers, handoff, README prose,
   and git state before assigning work.
3. Build or refresh the lane map: owned scopes, shared scopes, validation ladder, related repos,
   current maturity, target maturity, active/draft/deferred work, and lane-map/workstream drift.
4. Use inventory readiness issues to separate active queues from closed history and route missing
   context, TODO mismatch, and lane drift.
5. Run a source coverage audit before declaring any work ready.
6. Use `zoom-out`, `plan-architecture-lane`, and scoped `improve-codebase-architecture` when code
   understanding, seams, docs/code alignment, or future depth are unclear.
7. Create or revise lane roadmaps and draft workstreams only after evidence supports them.
8. Design lane campaigns: ordered medium goals with gates, stop conditions, autonomy, and horizon.
9. Recommend stable lane worktrees, exact prompts/goals, and which side effects the campaign may
   pre-approve.
10. After repair/closeout/recon, re-plan before assignment; while lanes run, do read-only reconnaissance without mutating active ledgers.

## Decision Policy

Default to recommendation, not interrogation. Ask the user only for product direction,
ADR/schema/public-contract changes, related-repo actions, or side effects not covered by an
approved campaign policy. Do not ask "what next?" when repo evidence can answer it.

Use `ASSIGN` only when a lane map, ready active/draft workstream or bundle, matching TODO/gates/source scope, and shared-scope decision are clear.
Closed/complete/completed workstreams and handoff follow-ons are candidate evidence only; without an active queue, report `Implementation Horizon: 0` and stay in `DISCOVERY` or `PLAN`.

## Lane Autonomy

Lane terminals may propose the next same-lane medium goal when their campaign finishes. They may
continue only inside an approved campaign or an explicit user-approved goal. They must stop for ADR,
schema, public contract, shared scope, failed gate, related-repo, or dirty unrelated-file issues.

## Output

Start with:

```md
## Program Action
Mode: DISCOVERY | SHAPE | PLAN | ASSIGN | RECON | DECISION
Now: <what this commander terminal should do next>
Why: <one sentence grounded in repo evidence>
```

Then include the recommended action, evidence read, lane map changes, terminal budget, metrics, `Autonomy Horizon`, campaign
candidates, parallelism/serial decision, required docs/ADR updates, proposed side-effect policy, worktree
recommendations, exact Codex goals to set after approval, prompts for lane terminals, and a
`Minimal User Input Needed` section listing only decisions that cannot be inferred from repo
evidence. Every lane/worker prompt must require final status `DONE | DONE_WITH_CONCERNS | BLOCKED |
NEEDS_CONTEXT`, changed files, validation, evidence updates, concerns/follow-ups, review/verify
readiness, and return to `integrate-lane-results`.

## Example

```text
Use $plan-engineering-program for nako. Review the current architecture lanes, active worktrees,
workstreams, and ADRs. Propose storage, transcode, and playback lane campaigns with stable
worktrees, allowed autonomy, validation gates, and exact Codex goals. Do not implement code.
```

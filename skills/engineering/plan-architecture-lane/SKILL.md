---
name: plan-architecture-lane
description: >
  Turns a selected Rust architecture direction into a docs/code-aligned workstream and lane plan
  before implementation. Use when a planner needs to choose planning depth, inspect docs/code
  alignment, decide whether to delegate to improve-codebase-architecture, create or reuse
  workstreams, or propose lane worktrees and lane goal bundles for capability areas such as
  storage, transcode, playback, realtime, server, or addons.
---

# Plan Architecture Lane

Use this after the user selects an architecture direction. This skill plans; it does not implement
code, create worktrees, rewrite docs, or mutate task ledgers without approval.

## Inputs

Require or infer:

- primary repo path,
- related repo paths,
- worktree root,
- selected direction or lane,
- user goal and non-goals,
- current architecture docs and workstreams,
- validation commands if known.

If product or domain direction is still unclear after reading docs/code, return to `grill-with-docs`
before planning.

## Read First

- `CONTEXT.md`, `AGENTS.md`, and relevant ADRs,
- `docs/architecture/`, `docs/workstreams/*/WORKSTREAM.json`, and active `TODO.md`,
- `Cargo.toml`, relevant crates/modules/tests, and obvious dependency direction,
- git status, `git worktree list`, branches, and related repo status.

Read `references/lane-deepening-backlog.md` when the user wants a lane to keep maturing over many
sessions, when ready tasks are too small to sustain a lane terminal, or when current work is blocked
by shared-scope conflicts and new same-lane candidates may exist. Also read it when the planner has
idle time after dispatching lane work and should perform read-only architecture reconnaissance.

Do not rely on chat history when repo docs or code disagree.

## Planning Depth Gate

- **Light planning**: docs and task ledger match the code. Reuse/open a workstream and propose lane
  goal bundles.
- **Code-aware planning**: the direction is known, but task boundaries need code evidence. Inspect
  relevant crates/modules/tests enough to name owned scopes, shared scopes, validation, and risks.
- **Architecture review planning**: lane seams, target state, or docs/code alignment are unclear.
  Delegate a scoped review to `improve-codebase-architecture` before opening or rewriting a
  workstream.

## Process

1. Restate the selected direction, goal, non-goals, and related repos.
2. Check whether architecture docs and workstreams match current code.
3. Run a source coverage audit using `../dev-flow/references/source-coverage-audit.md` before
   finalizing workstreams or lane bundles.
4. Choose planning depth and list the evidence for that choice.
5. If the ready queue is thin or workers are already dispatched, proactively perform read-only lane
   deepening discovery before reporting that no useful implementation work is available.
6. If architecture review is needed, delegate to `improve-codebase-architecture` with a narrow
   scope, summarize the best candidate, and ask only for a real tradeoff or side-effect approval.
7. For code-aware planning, use explorer subagents for independent code questions when available;
   treat their output as planning evidence, not durable state.
8. If docs and code are sufficient, recommend create/reuse workstream actions for `open-workstream`.
9. Propose worktree reuse/creation, branch names, lane goal bundles, Codex goals to set,
   validation, and terminal prompts for `plan-engineering-program`.

## Guardrails

- Recommend concrete worktrees and commands after analysis, but ask before side effects unless an
  approved campaign policy already covers them.
- Do not create one workstream per task.
- Do not assign lane terminals until owned scopes, shared scopes, validation, and stop conditions
  are explicit.
- Do not invent architecture decisions when ADRs or code evidence are missing.
- Promote durable decisions into `CONTEXT.md`, ADRs, architecture docs, or workstream docs.

## Output

Report planning depth, docs/code alignment, evidence read, missing context, whether
`improve-codebase-architecture` is needed, new deepening candidates classified by readiness,
workstream create/reuse recommendation, lane/worktree recommendation, draft lane goal bundles,
Codex goals to set for approved bundles/tasks, idle planner follow-up, terminal prompts, and
approval questions. When reporting through an upper planner terminal, use the report shape from
`plan-engineering-program`.

## Example

```text
Use $plan-architecture-lane for the nako storage lane. Check whether docs and code align, decide
whether scoped $improve-codebase-architecture is needed, then recommend workstreams, worktrees, and
lane goal bundles before implementation.
```

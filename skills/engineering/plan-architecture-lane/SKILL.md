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
code, create worktrees, or rewrite docs without approval.

## Inputs

Require or infer:

- primary repo path,
- related repo paths,
- worktree root,
- selected direction or lane,
- user goal and non-goals,
- current architecture docs and workstreams,
- validation commands if known.

If the direction is unclear, return to `grill-with-docs` before planning.

## Read First

- `CONTEXT.md`, `AGENTS.md`, and relevant ADRs,
- `docs/architecture/`, `docs/workstreams/*/WORKSTREAM.json`, and active `TODO.md`,
- `Cargo.toml`, relevant crates/modules/tests, and obvious dependency direction,
- git status, `git worktree list`, branches, and related repo status.

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
3. Choose planning depth and list the evidence for that choice.
4. If architecture review is needed, delegate to `improve-codebase-architecture` with a narrow
   scope and stop after the review report asks the user which candidate to explore.
5. For code-aware planning, use explorer subagents for independent code questions when available;
   treat their output as planning evidence, not durable state.
6. If docs and code are sufficient, recommend create/reuse workstream actions for `open-workstream`.
7. Propose worktree reuse/creation, branch names, lane goal bundles, Codex goals to set,
   validation, and terminal prompts for `coordinate-workstream`.

## Guardrails

- Recommend concrete worktrees and commands after analysis, but ask before executing side effects.
- Do not create one workstream per task.
- Do not assign lane terminals until owned scopes, shared scopes, validation, and stop conditions
  are explicit.
- Do not invent architecture decisions when ADRs or code evidence are missing.
- Promote durable decisions into `CONTEXT.md`, ADRs, architecture docs, or workstream docs.

## Output

Report planning depth, docs/code alignment, evidence read, missing context, whether
`improve-codebase-architecture` is needed, workstream create/reuse recommendation, lane/worktree
recommendation, draft lane goal bundles, Codex goals to set for approved bundles/tasks,
terminal prompts, and approval questions.

## Example

```text
Use $plan-architecture-lane for the nako storage lane. Check whether docs and code align, decide
whether scoped $improve-codebase-architecture is needed, then recommend workstreams, worktrees, and
lane goal bundles before implementation.
```

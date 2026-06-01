# Worktree Safety

Use this before assigning, executing, integrating, syncing, or closing multi-terminal work.

Worktree mistakes are expensive because the planner, lane terminals, and workers may all see
different filesystem roots and branch heads.

## Pre-Flight Snapshot

Capture before edits or side effects:

- absolute repo path and current working directory,
- `git rev-parse --show-toplevel`,
- `git status --short --branch`,
- current branch and `HEAD`,
- `git worktree list --porcelain`,
- intended lane, workstream, task, and campaign,
- dirty files classified as own-task, shared-scope, unrelated, or unknown.

If the repo root, branch, or worktree identity is ambiguous, stop before editing.

## Path Guard

- Use absolute paths in planner state and terminal prompts.
- Verify a path is inside the intended repo/worktree before recursive operations.
- Never delete or move a computed path unless its resolved absolute path is confirmed.
- Do not pass path lists between different shells for destructive operations.

## Branch And Scope Guard

- Prefer one stable worktree per long-lived architecture lane.
- Use branch names that include lane or campaign identity when practical.
- Do not continue when the current branch does not match the assigned lane or task.
- Do not commit unrelated dirty files; stage only the accepted task or bundle.
- Sync main only when campaign policy or explicit user approval allows it.

## Cwd Drift Sentinel

Before a significant command sequence, re-check:

```text
repo_root:
cwd:
branch:
head:
assigned_scope:
```

If `cwd` or branch changed unexpectedly, stop and report `BLOCKED_DECISION` or `NEEDS_CONTEXT`.

## Prune And Cleanup

Worktree cleanup is a side effect. Recommend cleanup when stale or orphaned worktrees exist, but ask
before deleting worktree directories or branches unless a future approved cleanup policy explicitly
covers that action.

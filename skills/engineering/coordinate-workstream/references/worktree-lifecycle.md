# Worktree Lifecycle

Use this when planning, creating, reusing, syncing, or retiring lane worktrees.

## Defaults

- Prefer one stable worktree per architecture lane.
- Do not use a main branch as a lane worktree branch.
- Keep the primary checkout on the project's mainline branch.
- Reuse lane worktrees across same-lane workstreams.
- Prefer short-lived branches per workstream or integration slice inside the stable lane worktree.

## Create Or Reuse

Before proposing creation:

- check `git worktree list`,
- check branch and dirty status,
- confirm lane ownership and validation path,
- propose path, branch name, and command,
- ask for user approval before executing.

## Sync And Retire

- Sync main into lane worktrees before starting a new queued workstream.
- Do not delete or clean worktrees without explicit approval.
- Retire a worktree only after its branch is integrated or intentionally abandoned.
- Mention Rust `target/` storage impact when proposing many worktrees.

## Output

Report worktree map, branch map, dirty status, proposed create/reuse/sync/retire actions, approval
questions, and commands to run after approval.

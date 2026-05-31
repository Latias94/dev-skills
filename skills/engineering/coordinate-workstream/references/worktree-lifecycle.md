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

- Before commit, merge, or sync, verify the current directory resolves inside the expected repo or
  worktree root, and that the branch matches the planner record when one exists.
- Do not run lane work on protected branches such as `main`, `master`, `develop`, `trunk`, or
  `release`.
- Treat dirty files outside the approved scope as a planner blocker. Commit only approved paths.
- Prefer relative paths. If an absolute path is used in a command or plan, confirm it resolves under
  the intended repo or worktree root.
- Do not use `git clean`, cross-worktree stash tricks, or reset/checkout/rebase recovery without
  explicit user approval and a planner recovery note.
- Sync main into lane worktrees before starting a new queued workstream.
- Sync main into active lane worktrees after any accepted lane branch is merged to main when other
  lanes may depend on it or shared scopes changed.
- Sync before starting a new lane bundle, before touching shared scopes, and before review/verify
  when the branch is far behind main.
- Do not interrupt a clean, isolated same-lane task solely to sync unless main contains a relevant
  dependency or the planner wants an integration checkpoint.
- Do not delete or clean worktrees without explicit approval.
- Retire a worktree only after its branch is integrated or intentionally abandoned.
- Mention Rust `target/` storage impact when proposing many worktrees.

## Output

Report worktree map, branch map, dirty status, proposed create/reuse/sync/retire actions, approval
questions, and commands to run after approval.

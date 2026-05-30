# Side-Effect Approval Matrix

Use this whenever a planner is about to move from analysis to filesystem, git, or repo-state side
effects.

## Usually Safe Without Approval

- Read docs, code, git status, diffs, and worktree lists.
- Run inventory scripts and targeted read-only analysis.
- Draft plans, lane bundles, terminal prompts, and Codex goals to set.
- Run validation commands when they do not mutate project state beyond normal build artifacts.
- Write local planner-state only after the file is already agreed to be local-only.

## Ask Before Doing

- Create, delete, move, or clean worktrees.
- Create, switch, merge, rebase, or delete branches.
- Edit ADRs, architecture docs, workstream target state, or global task order.
- Touch shared scopes outside an approved bundle.
- Commit, amend, tag, push, or merge.
- Change related repositories.
- Delete files, run cleanup commands, or remove build/cache directories.

## Approval Output

When approval is needed, present the concrete command or edit, why it is needed, expected effect,
rollback signal, and what will remain untouched.

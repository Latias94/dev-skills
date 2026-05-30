# Integration Protocol

Use this after result inspection, review, or verification says a task, bundle, or lane branch may be
accepted.

## States

- `ACCEPT_FOR_REVIEW`: request `review-workstream` before accepting.
- `NEEDS_VERIFY`: run `verify-rust-workstream` with fresh evidence.
- `READY_TO_INTEGRATE`: reviewed, verified, scoped, and ready for merge/sync planning.
- `NEEDS_FIX`: return to the worker or lane terminal with a bounded fix task.
- `BLOCKED`: user, ADR, shared scope, schema, or cross-repo decision required.

## Integration Steps

1. Confirm changed files match the approved scope.
2. Confirm task ledger, evidence, and handoff are updated.
3. Classify required documentation updates using `../dev-flow/references/documentation-authority.md`.
4. Run review and fresh verification before accepting completion.
5. Commit only approved changes when the user authorized commits.
6. Integrate one lane branch at a time.
7. Sync main back into active lane worktrees after integration.
8. Update planner state, lane queue, and next Codex goal to set.

## Cadence

Commit after review and fresh verification when the branch contains one accepted task, lane bundle,
or workstream slice with complete docs and evidence. Do not commit failed gates, unresolved
`DONE_WITH_CONCERNS`, missing evidence, or unrelated dirty files.

Merge back to main when the committed slice is reviewed, verified, user-approved, and either:

- another lane depends on it,
- it touched shared scopes,
- the current bundle/workstream slice is complete,
- branch divergence is becoming integration risk,
- or the planner is preparing a handoff/closeout.

Do not merge just because a worker said `DONE`; merge only after planner acceptance. If the next
same-lane task is isolated and no other lane depends on it, the planner may keep working on the lane
branch and defer merge until the approved bundle boundary.

## Output

Report integration state, branch/worktree, changed files, review status, verification status, merge
order, sync commands to propose, documentation updates, conflicts, follow-up splits, and the next
approved bundle. Use role-specific wording: "Planner now reviews/verifies/integrates" for work done
in the current planner terminal, and "Send to <role> terminal" only for prompts that should be
pasted elsewhere.

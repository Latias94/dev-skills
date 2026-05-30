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
3. Run review and fresh verification before accepting completion.
4. Commit only approved changes when the user authorized commits.
5. Integrate one lane branch at a time.
6. Sync main back into active lane worktrees after integration.
7. Update planner state, lane queue, and next Codex goal to set.

## Output

Report integration state, branch/worktree, changed files, review status, verification status, merge
order, sync commands to propose, conflicts, follow-up splits, and the next approved bundle.

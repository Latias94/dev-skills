# Integration Protocol

Use this after result inspection, review, or verification says a task, bundle, or lane branch may be
accepted.

## States

- `ACCEPT_FOR_REVIEW`: request `review-workstream` before accepting.
- `NEEDS_VERIFY`: run `verify-rust-workstream` with fresh evidence.
- `READY_TO_INTEGRATE`: reviewed, verified, scoped, and ready for merge/sync planning.
- `NEEDS_FIX`: return to the worker or lane terminal with a bounded fix task.
- `BLOCKED`: user, ADR, shared scope, schema, or cross-repo decision required.
- `READY_FOR_NEXT_BUNDLE`: accepted, integrated or intentionally deferred at a clean boundary, and
  ready for upper-planner or same-lane next-goal selection.

## Integration Steps

1. Confirm changed files match the approved scope.
2. Confirm task ledger, evidence, and handoff are updated.
3. Classify required documentation updates using `../dev-flow/references/documentation-authority.md`.
4. Run review and fresh verification before accepting completion.
5. Commit only approved changes when the user or campaign policy authorized commits.
6. Integrate one lane branch at a time.
7. Run a post-merge integration gate before declaring the slice integrated.
8. Sync main back into active lane worktrees after integration.
9. Update planner state, lane queue, and next Codex goal to set.
10. Return to `plan-engineering-program` for global sequencing or `run-architecture-lane` for an
    approved same-lane next bundle.

## Cadence

Auto-commit after review and fresh verification when the campaign policy allows it and the branch
contains one accepted task, lane bundle, or workstream slice with complete docs and evidence. Do not
commit failed gates, unresolved `DONE_WITH_CONCERNS`, missing evidence, or unrelated dirty files.

Merge back to main when the committed slice is reviewed, verified, authorized by user or campaign
policy, and either:

- another lane depends on it,
- it touched shared scopes,
- the current bundle/workstream slice is complete,
- branch divergence is becoming integration risk,
- or the upper planner is preparing a handoff/closeout.

Do not merge just because a worker said `DONE`; merge only after integrator acceptance. If the next
same-lane task is isolated and no other lane depends on it, the upper planner may keep working on
the lane branch and defer merge until the approved bundle boundary.

Stop before merge conflicts, failed post-merge gates, protected branch issues, unrelated dirty
files, or unapproved pushes. These conditions need user or upper-planner direction.

After merging to main, run the smallest gate that proves the integrated claim. For Rust projects,
prefer targeted `cargo nextest` package/filter gates first, then broader workspace or integration
gates when feasible. Record the command, result, and skipped-gate rationale before syncing active
worktrees or assigning dependent lane bundles.

## Output

Report integration state, branch/worktree, changed files, review status, verification status, merge
order, sync commands to propose, documentation updates, conflicts, follow-up splits, and the next
approved bundle. Use role-specific wording: "Integrator now reviews/verifies/integrates" for work
done in the current integration terminal, "Upper planner now updates the campaign" for program
planning work, and "Send to <role> terminal" only for prompts that should be pasted elsewhere.

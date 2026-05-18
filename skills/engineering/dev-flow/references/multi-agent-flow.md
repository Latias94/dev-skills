# Multi-Agent Flow

## Roles

**Planner**
: Owns the workstream, task ledger, dependency order, and conflict resolution.

**Worker**
: Owns one bounded task from the ledger.

**Reviewer**
: Checks implementation against both repository standards and workstream intent.

## Launch Criteria

Use multiple agents only when:

- tasks are independent enough to run in parallel,
- file scopes are disjoint or clearly serialized,
- validation can be run per task,
- and the planner can integrate results.

Keep the work local when the next step depends on one unresolved design decision.

## Parallel Work Pattern

1. Planner updates `TODO.md` with task IDs, owners, dependencies, scopes, and validation.
2. Each worker receives one task ID and an explicit file/module scope.
3. Workers update only:
   - their task status,
   - relevant evidence notes,
   - a journal entry or handoff.
4. Planner integrates results and resolves conflicts.
5. Reviewer uses `review-workstream` for contract and code-quality checks.
6. Planner uses `verify-rust-workstream` before accepting completion.

## Worker Prompt Shape

```text
You are Worker <id>. You are not alone in the codebase.
Own task <TASK-ID> from docs/workstreams/<slug>/TODO.md.
Do not rewrite global scope or unrelated tasks.
Do not revert user or other worker changes.
Touched file scope: <paths>.
Validation: <commands>.
Final status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT.
Final response: changed files, validation, evidence updates, concerns, next notes.
```

## Worker Status Protocol

- `DONE`: implementation and task-local validation completed.
- `DONE_WITH_CONCERNS`: completed, but reviewer/planner should inspect named concerns before accepting.
- `BLOCKED`: cannot finish without task split, design change, or external input.
- `NEEDS_CONTEXT`: needs missing repo, workstream, or requirement context before continuing.

## Stop Conditions

Stop and escalate to the planner when:

- the task requires changing an ADR or workstream target state,
- another worker owns the same file region,
- validation is impossible with the current task split,
- or the implementation reveals the task is the wrong vertical slice.

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
5. Reviewer checks standards and spec alignment.

## Worker Prompt Shape

```text
You are Worker <id>. You are not alone in the codebase.
Own task <TASK-ID> from docs/workstreams/<slug>/TODO.md.
Do not rewrite global scope or unrelated tasks.
Do not revert user or other worker changes.
Touched file scope: <paths>.
Validation: <commands>.
Final response: changed files, validation, blockers, next notes.
```

## Stop Conditions

Stop and escalate to the planner when:

- the task requires changing an ADR or workstream target state,
- another worker owns the same file region,
- validation is impossible with the current task split,
- or the implementation reveals the task is the wrong vertical slice.

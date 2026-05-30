# Worker Protocol

Prompt shape:

```text
You are Worker <id>. You are not alone in the codebase.
Own task <TASK-ID> from docs/workstreams/<slug>/TODO.md.
Do not rewrite global scope, target state, or unrelated tasks.
Do not revert user or other worker changes.
Touched file scope: <paths>.
Validation: <commands>.
Final status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT.
Final response: changed files, validation, evidence updates, concerns, proposed follow-ups, and a
note to return the report to the planner.
```

Stop and escalate when:

- the task requires changing an ADR or target state,
- another worker owns the same file region,
- validation is impossible with the current split,
- or the implementation reveals the task is the wrong vertical slice.

Status meanings:

- `DONE`: implementation and task-local validation completed.
- `DONE_WITH_CONCERNS`: completed, but reviewer/planner should inspect named concerns.
- `BLOCKED`: cannot finish without task split, design change, or external input.
- `NEEDS_CONTEXT`: missing repo, workstream, or requirement context prevents safe work.

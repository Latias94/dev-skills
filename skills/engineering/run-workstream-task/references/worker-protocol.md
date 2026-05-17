# Worker Protocol

Prompt shape:

```text
You are Worker <id>. You are not alone in the codebase.
Own task <TASK-ID> from docs/workstreams/<slug>/TODO.md.
Do not rewrite global scope or unrelated tasks.
Do not revert user or other worker changes.
Touched file scope: <paths>.
Validation: <commands>.
Final response: changed files, validation, blockers, next notes.
```

Stop and escalate when:

- the task requires changing an ADR or target state,
- another worker owns the same file region,
- validation is impossible with the current split,
- or the implementation reveals the task is the wrong vertical slice.

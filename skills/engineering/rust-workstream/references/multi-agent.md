# Multi-Agent Coordination

## Roles

**Planner**
: Owns scope, task decomposition, dependency order, and closeout.

**Worker**
: Owns one bounded task with explicit file scope and validation.

**Reviewer**
: Reviews against both the workstream contract and repository standards.

## Assignment Rules

- Assign disjoint file scopes when possible.
- If two workers must touch the same file, serialize those tasks or name the expected edit regions.
- Workers should not reformat unrelated files.
- Workers should record touched files and validation results.

## Journal Rules

Put session history in `JOURNAL/YYYY-MM-DD-<agent-or-topic>.md`.

Journal entries should include:

- task IDs touched,
- files changed,
- commands run,
- decisions proposed,
- blockers,
- next recommended action.

Do not store architectural truth only in a journal. Promote durable decisions into ADRs or
workstream docs.

## Conflict Handling

Stop and escalate when:

- an ADR conflicts with workstream design,
- two tasks require incompatible ownership of the same module,
- a worker discovers the task is not independently validatable,
- validation requires broad commands that are too slow or flaky without user approval.

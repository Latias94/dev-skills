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
你是 Worker <id>。你不是这个代码库里唯一工作的 agent。
负责 docs/workstreams/<slug>/TODO.md 里的任务 <TASK-ID>。
不要重写全局范围或无关任务。
不要回退用户或其他 worker 的变更。
可修改文件范围：<paths>。
验证命令：<commands>。
最终回复：变更文件、验证结果、阻塞项、下一步备注。
```

## Stop Conditions

Stop and escalate to the planner when:

- the task requires changing an ADR or workstream target state,
- another worker owns the same file region,
- validation is impossible with the current task split,
- or the implementation reveals the task is the wrong vertical slice.

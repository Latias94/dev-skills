# Worker Protocol

Prompt shape:

```text
你是 Worker <id>。你不是这个代码库里唯一工作的 agent。
负责 docs/workstreams/<slug>/TODO.md 里的任务 <TASK-ID>。
不要重写全局范围或无关任务。
不要回退用户或其他 worker 的变更。
可修改文件范围：<paths>。
验证命令：<commands>。
最终回复：变更文件、验证结果、阻塞项、下一步备注。
```

Stop and escalate when:

- the task requires changing an ADR or target state,
- another worker owns the same file region,
- validation is impossible with the current split,
- or the implementation reveals the task is the wrong vertical slice.

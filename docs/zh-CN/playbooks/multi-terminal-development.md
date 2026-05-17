# 多终端开发

English: [../../playbooks/multi-terminal-development.md](../../playbooks/multi-terminal-development.md)

当一个 workstream 需要多个 Codex 终端时，使用这个 playbook。

## 终端分工

```text
终端 1：Planner / PM
终端 2：Worker A
终端 3：Worker B
终端 4：Reviewer
终端 5：Docs / next-version planning
```

Planner 终端是唯一拥有全局 task ledger 的终端。

## Planner Prompt

```text
使用 $coordinate-workstream 协调当前 workstream。
读取 WORKSTREAM.json、TODO.md、HANDOFF.md、EVIDENCE_AND_GATES.md、最新 JOURNAL 条目和 git status。
只分配 ready 的任务，并明确 owner、文件范围、依赖关系和验证命令。
整合 worker 汇报，并决定继续执行、进入 review、关闭、拆分 follow-on，还是 handoff。
```

## Worker Prompt

```text
使用 $run-workstream-task 执行 docs/workstreams/<slug>/TODO.md 里的任务 <TASK-ID>。
你是 Worker <id>。你不是这个代码库里唯一工作的 agent。
保持在分配的文件范围内。
不要重写全局计划。
不要回退用户或其他 worker 的变更。
汇报变更文件、验证结果、阻塞项和 handoff notes。
```

## Reviewer Prompt

```text
根据 workstream 的 DESIGN.md、TODO.md、EVIDENCE_AND_GATES.md、仓库 AGENTS.md 和相关 ADR
review 已完成的 worker tasks。先报告 findings，再报告残余风险和缺失 gates。
```

## Docs / Next-Version Prompt

```text
使用 $grill-with-docs 或 $to-prd 准备下一版本方案。
不要重写当前 active workstream 的目标或 TODO.md。
产出 ADR candidates、PRD/spec notes、prototype findings，或 proposed follow-on workstream。
```

## 集成规则

Worker 更新自己的 task notes、evidence notes、journal/handoff entries。Planner 负责把结果集成到全局任务顺序、owner 分配、milestone 状态和 closeout 决策。

## 停止条件

出现以下情况时，停止并行执行，回到 planner 协调：

- 两个 worker 需要同一片文件区域。
- 任务改变 workstream target state。
- 任务暴露 ADR 级别决策。
- 验证无法独立运行。
- worker 输出和 workstream contract 冲突。

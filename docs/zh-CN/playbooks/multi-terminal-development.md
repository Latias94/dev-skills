# 多终端开发

English: [../../playbooks/multi-terminal-development.md](../../playbooks/multi-terminal-development.md)

当一个 workstream 需要多个 Codex 终端，或大型项目采用每个架构域一个终端时，使用这个 playbook。

如果你不确定仓库是否需要这种协调强度，先运行 `$audit-project-scale`；小型或中型工作继续用
`$dev-flow`。

## 终端分工

```text
终端 1：Planner / PM
终端 2：Worker A
终端 3：Worker B
终端 4：Reviewer
终端 5：Verifier / closeout
终端 6：Docs / next-version planning
```

Planner 可以是一个单独终端，也可以是你的主控终端。它是唯一负责全局顺序、shared-scope
决策和 task ledger 的终端。

对于 architecture lane 工作，Planner 负责跨 lane 优先级和 shared scopes。Lane 终端负责
storage、transcode、playback、realtime 或 admin 这类能力域。

## Planner 状态

多 worktree 工作中，把运行态放在本地 `.codex/planner-state.local.json` 或
`docs/local/PLANNER_STATE.md`。记录 repo path、branch、head、dirty status、lane/workstream、
active task、shared scopes、validation 和 related repositories。只提交示例和 lane 名称，不提交
个人机器上的绝对路径。

## Planner 发现 Prompt

当你还不知道当前应该跑哪个 workstream 或 lane 时，用这个。

```text
使用 $coordinate-workstream 检查这个仓库，并推荐多终端计划。
不要假设已经存在 current workstream。
读取 docs/architecture/LANES.md、WORKSTREAM_LINKS.md、docs/workstreams/*/WORKSTREAM.json、
git status、git worktree list，以及文档中提到的相关仓库。
汇报候选 active workstreams 或 lanes、推荐终端、已有或建议创建的 worktree 路径、分支同步阻塞项、
建议的创建命令、终端提示词，以及每个终端应该先跑的任务。用户批准前，不要创建新 worktree 或分支。
```

## 已知 Workstream Planner Prompt

当 workstream 路径已经明确时，用这个。

```text
使用 $coordinate-workstream 协调 docs/workstreams/<slug>。
读取 WORKSTREAM.json、TODO.md、HANDOFF.md、EVIDENCE_AND_GATES.md、最新 JOURNAL 条目和 git status。
只分配 ready 的任务，并明确 owner、文件范围、依赖关系和验证命令。
整合 worker 状态汇报，安排 review 和新鲜验证，并决定继续执行、关闭、拆分 follow-on，还是 handoff。
```

已知 Architecture lane planner prompt：

```text
使用 $coordinate-workstream 协调 architecture lanes。
读取 docs/architecture/LANES.md、active WORKSTREAM.json、git status、branches 和 worktrees。
批准哪个 lane 继续、哪个 lane 需要同步 main、哪个 lane 被 shared scopes 阻塞。
已完成 workstream 必须经过 review 和新鲜验证后，再逐个集成。
```

## Workstream 过多

先把 workstream 过多当作状态治理问题处理，不要急着改目录结构：

- 保持 `docs/workstreams/<slug>/` 扁平，用 metadata/index 做 lane 分组。
- 分配终端前先盘点 `WORKSTREAM.json`。
- 开新 workstream 前，先关闭或拆分过时的 `active` workstreams。
- 每个 lane 只保留短 active queue，其余推迟。
- 不要随意移动旧 workstream 路径，除非链接和 ADR 引用都能保持稳定。

## 创建终端

Planner 负责推荐终端、worktree 路径、分支名、创建命令和提示词。它可以在用户批准后帮忙创建
worktree，也可以把命令交给用户执行。只有用户批准且角色有明确范围和验证路径时，才创建终端。

优先保持一个 architecture lane 一个长期 worktree，不要每个 workstream 新建一个 worktree。
在同一个 lane worktree 里连续推进队列，可以减少分支杂音、合并成本和 Rust `target/` 空间增长。

- Planner / 主控终端：发现 active work，负责顺序、冲突和终端分配。
- Architecture lane 终端：长期负责一个能力域下的 workstream 队列。
- Worker 终端：只负责 `TODO.md` 里的一个有边界任务。
- Reviewer / verifier 终端：产出量大时单独开；否则 planner 可以负责 review 和验证。
- Docs / next-version 终端：探索未来计划，但不能重写当前 active ledger。

## Architecture Lane Prompt

```text
使用 $run-architecture-lane 负责 <lane> lane。
保持这个终端在该 lane 的 worktree 中，持续推进该能力域下的 workstream 队列；遇到 shared scopes、ADR 变更、schema 变更或 server 契约变更时停止并请求 planner 协调。
```

## Worker Prompt

```text
使用 $run-workstream-task 执行 docs/workstreams/<slug>/TODO.md 里的任务 <TASK-ID>。
你是 Worker <id>。你不是这个代码库里唯一工作的 agent。
保持在分配的文件范围内。
不要重写全局计划。
不要回退用户或其他 worker 的变更。
最终状态必须是 DONE、DONE_WITH_CONCERNS、BLOCKED 或 NEEDS_CONTEXT。
汇报变更文件、验证结果、evidence updates、concerns、阻塞项、handoff notes，以及推荐的同 lane 下一步。
不要自行决定全局下一个任务。
```

## Reviewer Prompt

```text
使用 $review-workstream 根据 workstream 的 DESIGN.md、TODO.md、EVIDENCE_AND_GATES.md、仓库
AGENTS.md 和相关 ADR review 已完成的 worker tasks。先报告 findings，再报告残余风险和缺失 gates。
```

## Verifier Prompt

```text
使用 $verify-rust-workstream 用新鲜命令证据验证已 review 的任务或 lane，然后 planner 才能标记完成。
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

# 使用说明

English: [../usage.md](../usage.md)

大多数时候，从 `$dev-flow` 开始。

`$dev-flow` 是总入口。它应该主动委托给下一个合适的 skill，而不是只告诉用户下一步该用哪个 skill。

当仓库陌生、旧工作流文档可能过时，或者你在判断是否值得开多终端和 architecture lanes 时，先用
`$audit-project-scale`。

大型项目里，如果一个终端需要长期负责 storage、transcode、playback、realtime 或 admin 这类能力域，
使用 `$run-architecture-lane`。

## 按仓库规模选择

| 情况 | 调用的 skill | 说明 |
| --- | --- | --- |
| 小仓库、一个有边界的变更 | `$dev-flow` | 让它路由到 `tdd` 或 `diagnose`，避免重文档。 |
| 中型仓库、多步骤变更 | `$dev-flow` | 需要可追溯性时打开或复用一个 workstream。 |
| 大型仓库、按能力域拆 worktree | `$audit-project-scale` 先行 | 优先一个 lane 一个长期 worktree；planner 创建前先询问。 |
| 多个终端已经活跃 | `$coordinate-workstream` | planner 可以是独立终端，也可以是你的主控终端。 |
| workstream 过多 | `$coordinate-workstream` | 先盘点，关闭过时 active，只保留短 active queue。 |
| 旧 workstream 或 architecture 文档 | `$audit-project-scale` | 先修复工作流基底，再新增 workstream。 |

## 常用调用

初始化项目：

```text
使用 $dev-flow 为这个 Rust 仓库初始化 dev-skills 工作流。
```

审计工作流规模：

```text
使用 $audit-project-scale 审计这个 Rust 仓库。判断它应该保持轻量、使用普通 workstreams，
还是加入 architecture lanes 和 planner 协调。
```

规划大功能：

```text
使用 $dev-flow 规划这个功能。如果需求还不清楚，先澄清需求；然后创建或复用合适的
workstream，并拆分可执行任务。
```

规划选定子架构方向：

```text
使用 $dev-flow 规划 storage lane。先选择 planning depth，检查 docs/code 是否对齐，
并在创建 workstream 或 lane bundle 前路由到 $plan-architecture-lane。
```

执行一个有边界的任务：

```text
使用 $dev-flow 执行 docs/workstreams/<slug>/TODO.md 里的任务 ABC-020。
```

诊断失败：

```text
使用 $dev-flow 诊断这个失败测试，并把回归证据记录到当前 workstream。
```

准备 handoff：

```text
使用 $dev-flow 为当前 workstream 准备 handoff。
```

发现多终端计划：

```text
使用 $coordinate-workstream 检查这个仓库，识别 active workstreams 或 architecture lanes，
并推荐 planner、lane、worker、reviewer 和 docs 终端。优先一个 architecture lane 一个长期
worktree，创建 worktree 或分支前必须询问用户。
```

协调一个已知 workstream：

```text
使用 $coordinate-workstream 协调 docs/workstreams/<slug>，覆盖 planner、worker、reviewer 和 docs 终端。
```

协调 architecture lanes：

```text
使用 $coordinate-workstream 协调 architecture lanes、shared scopes、分支同步和已完成 workstream 的集成。
```

盘点大量 workstreams：

```text
使用 $coordinate-workstream 盘点 docs/workstreams，按 lane 汇总 active/draft workstreams，
找出过时或缺 lane metadata 的项目，并建议哪些关闭、保留 active、或推迟。
```

检查已完成 worktree 结果：

```text
使用 $coordinate-workstream 检查 worktree F:\SourceCodes\Rust\nako-worktrees\<lane-worktree> 的结果。
读取 git status、git diff、相关 workstream TODO/evidence/handoff，以及必要的终端报告或 session id。
判断结果是 ACCEPT_FOR_REVIEW、NEEDS_FIX、NEEDS_VERIFY、BLOCKED 还是 READY_FOR_NEXT_BUNDLE。
然后给出 Planner 下一步、要设置的 Codex goal 和终端提示词。不要让 worker 决定全局下一个任务。
```

运行长期架构终端：

```text
使用 $run-architecture-lane 负责 storage lane。让这个终端持续处理 storage/VFS workstreams；遇到数据库或 server 共享契约变更时停止并请求协调。
```

review 并验证任务：

```text
使用 $dev-flow review 并验证任务 ABC-020，然后再标记完成。
```

恢复异常 Codex 会话：

```text
使用 $codex-session-recovery 从 latest Codex session 恢复上下文。
```

## 直接调用 Matt Pocock Skills

当你明确要做某个专项动作时，直接调用这些 skill。

配置 issue tracker / domain docs：

```text
使用 $setup-matt-pocock-skills 为这个仓库配置 AGENTS.md 和 docs/agents。
```

在项目文档存在前拷问一个想法：

```text
使用 $grill-me 拷问这个项目想法，直到 MVP、非目标和风险都足够明确。
```

根据现有文档压力测试方案：

```text
使用 $grill-with-docs 根据 CONTEXT.md、ADR 和当前 workstream 压力测试这个方案。
```

理解陌生代码：

```text
使用 $zoom-out 解释这个子系统如何融入整个项目。
```

审查架构：

```text
使用 $improve-codebase-architecture 查找 crate 边界、模块深度和可测试性问题。
```

执行架构重构：

```text
使用 $fearless-refactor 处理架构报告里的最高优先级建议，并通过 $dev-flow 承接执行。
```

准备发布日志：

```text
使用 $changelog 根据 latest tag 到 HEAD 的变更更新 CHANGELOG.md。
```

做可丢弃原型：

```text
使用 $prototype 在写入 ADR 前测试两种设计。
```

导出到项目 tracker：

```text
使用 $to-prd 把这个已澄清方案整理成 PRD；如果需要进入 GitHub Issues，再使用 $to-issues。
```

创建可复用 skill：

```text
使用 $write-a-skill 为这个重复工作流创建一个项目专属 skill。
```

## 手动恢复 Skill

`$codex-session-recovery` 应该在 Codex 崩溃、上下文损坏、`invalid_encrypted_content`，或新
会话需要恢复旧会话上下文时由用户主动调用。它读取 Codex session JSONL 并输出恢复线索；
项目文档和 git 状态仍然高于恢复出来的聊天记录。

```text
使用 $codex-session-recovery 读取这个 Codex session id，恢复 active goal、最近工具调用、compaction summary 和安全继续方案：019e2779-da60
```

## 默认体验

```text
User -> $dev-flow -> delegated skill -> $dev-flow resumes routing
```

用户不需要记住内部工作流 skill。`$dev-flow` 应该决定下一步是 bootstrap、grill、
workstream planning、TDD execution、diagnosis、review 还是 handoff。
当问题本身是“这个仓库应该用多重的工作流”时，用 `$audit-project-scale`。
`$run-architecture-lane` 是大型项目长期架构终端的另一个默认入口。

## Codex Goals

Codex goal 适合绑定到 workstream task ledger 里的一个具体任务，或 Planner 批准的一个
lane goal bundle。

适合：

- `TODO.md` 里的一个 task ID
- 一个 Planner 批准的 lane goal bundle
- 一个单独 bug fix
- 一个有边界的验证循环

不适合：

- 整个 workstream
- 整个 architecture lane
- 长期架构记忆
- 替代 ADR 或 workstream docs

推荐模式：

```text
1. $open-workstream 创建任务 ABC-020。
2. 用户让 Codex 把 ABC-020 设置为当前 goal。
3. Agent 执行并验证这个任务。
4. 只有任务真正完成后，agent 才标记 goal complete。
5. Agent 更新 TODO.md 和 EVIDENCE_AND_GATES.md。
```

Lane bundle 模式：

```text
1. Planner 批准 bundle storage-20260530-01，里面包含 task IDs、scope、context、validation 和 stop conditions。
2. 用户让 lane 终端把这个 bundle 设置为当前 Codex goal。
3. Lane 终端一直运行，直到 bundle 完成或触发 stop condition。
4. Lane 终端汇报 DONE、DONE_WITH_CONCERNS、BLOCKED 或 NEEDS_CONTEXT。
5. Planner review、verify，并决定下一步全局动作。
```

## 内部工作流 Skills

这些通常由 `$dev-flow` 调用，不需要用户手动调用：

- `setup-rust-workstreams`
- `open-workstream`
- `plan-architecture-lane`
- `coordinate-workstream`
- `resume-workstream`
- `run-workstream-task`
- `review-workstream`
- `verify-rust-workstream`
- `close-workstream`

只有在你明确要绕过路由器，或 planner 终端正在用 `coordinate-workstream` 协调多终端时，才直接调用它们。

## 多 Agent 使用

只有当任务边界清楚时才并行。

Planner prompt：

```text
使用 $coordinate-workstream 检查这个仓库，并准备多终端计划。
不要假设已经存在 current workstream。只有在范围、分支、依赖关系和验证命令都明确时，才推荐终端和分配任务。
优先一个 architecture lane 一个长期 worktree。创建 worktree 或分支前必须询问，并给出 lane goal bundles、建议命令、context manifests、批准后要设置的 Codex goals 和终端提示词。
Planner 负责创建或复用 workstream、task ledger、lane bundles 和全局顺序；lane / worker 终端只实现分配的工作并回报。
创建 workstream 或 bundle 前用 $plan-architecture-lane 选择 planning depth；lane seams / docs/code 对齐不清楚时它可以转到 $improve-codebase-architecture。
写出每个已批准 task 或 lane bundle 要设置的精确 Codex goal，不要给整个 lane 设置 goal。
worktree、branch、commit、merge、push、shared-scope 或 related-repo side effects 前必须询问用户。
```

大型多 worktree 工作中，planner 可以把运行态存在 `.codex/planner-state.local.json`；
不要提交个人机器上的绝对路径。这个状态可以包含 terminal IDs、用于恢复的 session refs、
lane goal bundles 和 context manifests。Session refs 只是指针，不是事实源。

Worker prompt：

```text
使用 $run-workstream-task 执行任务 ABC-020。它应该按需委托给 $tdd 或 $diagnose，
编辑前读取分配的 context，保持在分配的文件范围内，完成后更新 task ledger 和 journal，并推荐同 lane 下一步。
不要自行决定全局下一个任务。
follow-up 或 split 建议写到最终汇报里，不要直接改变 workstream target state。
最后提醒用户把报告交回 Planner，由 Planner 安排 review、verification 和下一个批准的 task 或 bundle。
```

Reviewer prompt：

```text
使用 $review-workstream 根据 workstream contract 和仓库标准 review 已完成任务 ABC-020。
```

Verifier prompt：

```text
使用 $verify-rust-workstream 用新鲜命令证据验证任务 ABC-020，然后再标记完成。
```

Workers 不应重写全局 task ledger 或重新定义 workstream 目标状态。

## Skill Delegation

当一个 skill 委托给另一个 skill 时，传递最小且持久的上下文：

- workstream path
- task ID
- file scope
- context manifest 或 task-specific context
- validation command
- relevant ADR/docs
- expected output artifact

示例：

```text
Delegate to $tdd:
Task: ABC-020
Workstream: docs/workstreams/<slug>
Scope: crates/foo/src/**
Validation: cargo nextest run -p foo abc_020
Expected output: code changes, passing validation, TODO.md status update, evidence note
```

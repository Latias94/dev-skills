# 使用说明

English: [../usage.md](../usage.md)

大多数时候，从 `$dev-flow` 开始。

`$dev-flow` 是总入口。它应该主动委托给下一个合适的 skill，而不是只告诉用户下一步该用哪个 skill。

当仓库陌生、旧工作流文档可能过时，或者你在判断是否值得开多终端和 architecture lanes 时，先用
`$audit-project-scale`。

当输入还只是产品愿景，而不是明确工程 lane 时，使用 `$shape-product-architecture`。它会先把愿景、
参考产品、MVP 阶段、能力边界和 ADR candidates 变成规划文档，再进入 workstream。

大型项目里，如果一个终端需要长期负责 storage、transcode、playback、realtime 或 admin 这类能力域，
使用 `$run-architecture-lane`。

## 按仓库规模选择

| 情况 | 调用的 skill | 说明 |
| --- | --- | --- |
| 宽泛产品目标或 MVP 不清楚 | `$shape-product-architecture` | 先整理 vision、MVP ladder、capability map、lanes 和 ADR candidates。 |
| 小仓库、一个有边界的变更 | `$dev-flow` | 让它路由到 `tdd` 或 `diagnose`，避免重文档。 |
| 中型仓库、多步骤变更 | `$dev-flow` | 需要可追溯性时打开或复用一个 workstream。 |
| 大型仓库、按能力域拆 worktree | `$audit-project-scale` 先行 | 优先一个 lane 一个长期 worktree；上层 planner 创建前先询问。 |
| 多个终端已经活跃 | `$plan-engineering-program` / `$integrate-lane-results` | 上层 planner 负责后续 campaign；integrator 负责完成输出。 |
| workstream 过多 | `$plan-engineering-program` | 先盘点，关闭过时 active，只保留短 active queue。 |
| 旧 workstream 或 architecture 文档 | `$audit-project-scale` | 先修复工作流基底，再新增 workstream。 |

## 常用调用

初始化项目：

```text
使用 $dev-flow 为这个 Rust 仓库初始化 dev-skills 工作流。
```

审计工作流规模：

```text
使用 $audit-project-scale 审计这个 Rust 仓库。判断它应该保持轻量、使用普通 workstreams，
还是加入 architecture lanes 和上层 planner 协调。
```

规划大功能：

```text
使用 $dev-flow 规划这个功能。如果需求还不清楚，先澄清需求；然后创建或复用合适的
workstream，并拆分可执行任务。
```

塑造产品架构：

```text
使用 $shape-product-architecture 把这个产品目标整理成有边界的 vision、MVP ladder、
capability map、architecture lanes、ADR candidates 和初始 workstream 优先级。
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
使用 $plan-engineering-program 检查这个仓库，识别 active workstreams 或 architecture lanes，
并推荐上层 planner、lane、worker、reviewer 和 docs 终端。优先一个 architecture lane 一个长期
worktree，创建 worktree 或分支前必须询问用户。
```

规划一个已知 workstream：

```text
使用 $plan-engineering-program 规划 docs/workstreams/<slug>，明确上层 planner、lane、worker、reviewer 和 docs 终端如何分工。
```

规划 architecture lanes：

```text
使用 $plan-engineering-program 规划 architecture lanes、shared scopes、分支同步和后续 campaign。
```

盘点大量 workstreams：

```text
使用 $plan-engineering-program 盘点 docs/workstreams，按 lane 汇总 active/draft workstreams，
找出过时或缺 lane metadata 的项目，并建议哪些关闭、保留 active、或推迟。
```

检查已完成 worktree 结果：

```text
使用 $integrate-lane-results 检查 worktree F:\SourceCodes\Rust\nako-worktrees\<lane-worktree> 的结果。
先读取 git status、git diff、相关 workstream TODO/evidence/handoff、本地 planner state 和 session tail，再考虑是否需要用户报告。
先用 integrate-lane-results helper 检查这个 worktree，不要先让我手动复制聊天：
skills/engineering/integrate-lane-results/scripts/inspect_worktree_result.py <worktree> --json
判断结果是 ACCEPT_FOR_REVIEW、NEEDS_FIX、NEEDS_VERIFY、READY_TO_INTEGRATE、BLOCKED 还是 READY_FOR_NEXT_BUNDLE。
然后给出 integration 下一步、要设置的 Codex goal，以及给 lane/worker 终端的结构化 handoff block。
只有本地证据无法重建结果时，才让我粘贴聊天。不要让 worker 决定全局下一个任务。
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

## 直接调用专项 Skills

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

提交已 review 的工作：

```text
使用 $commit-work 只提交已 review 的 workstream 变更。检查所有 dirty files，只 stage 已批准路径，使用 Conventional Commits，运行相关检查，并汇报剩余 dirty files。
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
`$run-architecture-lane` 是大型项目长期架构终端的默认入口。`$shape-product-architecture`
是产品 / MVP / capability shaping 问题的默认入口。

当下一步不明显时，agent 应该说明当前阶段、推荐路线、已读取的证据、需要批准的 side effects、
预期产物或终端 prompt，以及下一个可能阶段。优先给出具体建议，而不是让用户在内部 skills 中选择。

## Codex Goals

Codex goal 适合绑定到 workstream task ledger 里的一个具体任务、已批准的一个 lane goal bundle，
或已批准的 lane campaign。

当任务、lane bundle 或 lane campaign 已经足够清楚、适合较长时间自动执行时，上层 planner 或 lane 输出应该给出精确 goal
文本，并明确询问是否由当前终端设置。如果当前对话里用户已经批准设置 goal，就直接设置这个有边界 goal。
不要要求用户自己意识到这里适合用 goal。

适合：

- `TODO.md` 里的一个 task ID
- 一个已批准的 lane goal bundle
- 一个带有序 bundles 和 auto-advance gates 的已批准 lane campaign
- 一个单独 bug fix
- 一个有边界的验证循环

不适合：

- 整个 workstream
- 整个 architecture lane
- 长期架构记忆
- 替代 ADR 或 workstream docs

长期 lane 深化应该让上层 planner 维护 lane roadmap 或 architecture doc，记录 current state、target
maturity、capability gaps、active/draft/deferred workstreams、validation ladder、shared scopes
和 next bundles。Codex goal 仍然只绑定当前 bundle；当多个 ready bundles 已经有序且 gates 清楚时，
上层 planner 可以改为提出 lane campaign，让一个 goal 带 checkpoint 和 stop conditions 跑得更久。

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
1. 上层 planner 批准 bundle storage-20260530-01，里面包含 task IDs、scope、context、validation 和 stop conditions。
2. 用户让 lane 终端把这个 bundle 设置为当前 Codex goal。
3. Lane 终端一直运行，直到 bundle 完成或触发 stop condition。
4. Lane 终端写出结构化 handoff block，状态为 DONE、DONE_WITH_CONCERNS、BLOCKED 或 NEEDS_CONTEXT。
5. Integrator review、verify，并和上层 planner 按需决定下一步全局动作。
```

Lane campaign 模式：

```text
1. 上层 planner 准备 campaign storage-20260531-01，包含有序 bundle queue、gates、checkpoints 和 stop conditions。
2. 用户让 lane 终端把这个 campaign 设置为当前 Codex goal。
3. Lane 终端只有在每一步 gate 通过时，才自动推进下一个 bundle。
4. 遇到失败 gates、shared scopes、ADR/schema/contract 变更、缺失 context 或未批准 side effects 时停止，并写出结构化 handoff block。
5. Integrator review、verify、integrate，并按需让上层 planner 刷新下一个 campaign。
```

当任务有依赖顺序且不适合并行时，用 serial lane campaign。它应该让一个终端在一个 worktree 上连续
执行，并且每一步 gate 和 evidence 通过后才自动推进。

## 内部工作流 Skills

这些通常由 `$dev-flow` 调用，不需要用户手动调用：

- `setup-rust-workstreams`
- `open-workstream`
- `plan-architecture-lane`
- `plan-engineering-program`
- `integrate-lane-results`
- `resume-workstream`
- `run-workstream-task`
- `review-workstream`
- `verify-rust-workstream`
- `close-workstream`

只有在你明确要绕过路由器，或上层 planner 终端正在用 `plan-engineering-program` 规划多终端时，才直接调用它们。

## 多 Agent 使用

只有当任务边界清楚时才并行。

上层 planner prompt：

```text
使用 $plan-engineering-program 检查这个仓库，并准备多终端计划。
先输出 Program Action 的 Mode、Now 和 Why。
不要假设已经存在 current workstream。只有在范围、分支、依赖关系和验证命令都明确时，才推荐终端和分配任务。
优先一个 architecture lane 一个长期 worktree。创建 worktree 或分支前必须询问，并给出 lane goal bundles、建议命令、context manifests、批准后要设置的 Codex goals 和终端提示词。
仓库支持时列出 3-5 个大的候选方向，但默认最多激活 3 个 lane / worker 终端。架构基底、lane map 或模块边界还不清楚时，用一个 planner/recon 终端或一个 serial campaign。
同时输出 WIP 数量、assignment go/no-go、预计 autonomy horizon 和 integration bottleneck 风险。
对于长期 campaign，提前选择 side-effect policy：`manual`、`auto-commit-sync` 或
`auto-commit-sync-merge`；同时列出冲突、失败 gates、无关 dirty files、ADR/schema/public
contract 变化、related-repo 决策、protected branch 问题和未批准 push 的禁止规则。
上层 planner 负责创建或复用 workstream、task ledger、lane bundles 和全局顺序；lane / worker 终端只实现分配的工作并回报。
创建 workstream 或 bundle 前用 $plan-architecture-lane 选择 planning depth；lane seams / docs/code 对齐不清楚时它可以转到 $improve-codebase-architecture。
当 lane 队列太薄时，先刷新 lane backlog，再分配更多工作。不要只消费已有 TODO；主动检查
code/docs，并提出同 lane 深化候选，分类为 implement-now、plan-first、ADR-first、
wait-for-active-branch 或 defer。
分配 worker 或 lane 终端后，如果没有 pending integration/review 工作，上层 planner 可以用空档做只读
architecture reconnaissance。scoped $improve-codebase-architecture 可以检查全仓库或单个 lane，
但结果只是 proposed candidates，不能未经批准直接改 active ledger 或 ADR。
先花 agent 时间，再消耗用户注意力。陌生代码用 $zoom-out，lane 队列太薄或 docs/code drift
用 $improve-codebase-architecture；只有真正的产品或领域决策不清楚时，才用 $grill-with-docs。
根据当前状态选择 Program Action mode：DISCOVERY、SHAPE、PLAN、ASSIGN、RECON 或 DECISION。
如果候选任务不能并行，但可以按依赖顺序连续执行，优先提出一个稳定 worktree 上的 serial lane
campaign，而不是不断让用户复制单任务 prompt。
写出每个已批准 task、lane bundle 或 lane campaign 要设置的精确 Codex goal，不要给整个 lane 设置 goal。
对于清楚的深度工作，优先提出 lane campaign，而不是让用户不断粘贴很小的 bundle。
只有未被 campaign policy 覆盖的 worktree、branch、commit、merge、push、shared-scope、related-repo side effects，或真正的产品/架构决策，才在给出最佳建议后询问用户。
```

大型多 worktree 工作中，上层 planner / integrator 可以把运行态存在 `.codex/planner-state.local.json`；
不要提交个人机器上的绝对路径。这个状态可以包含 terminal IDs、用于恢复的 session refs、
lane goal bundles 和 context manifests。Session refs 只是指针，不是事实源。

Worker prompt：

```text
使用 $run-workstream-task 执行任务 ABC-020。它应该按需委托给 $tdd 或 $diagnose，
编辑前读取分配的 context，保持在分配的文件范围内，完成后更新 task ledger 和 journal，并推荐同 lane 下一步。
不要自行决定全局下一个任务。
follow-up 或 split 建议写到最终汇报里，不要直接改变 workstream target state。
最后提醒用户把报告交回上层 planner 或 integrator，由其安排 review、verification 和下一个批准的 task 或 bundle。
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

# Dev Skills

面向 Rust 项目的可复用 Codex skills，覆盖小仓库到大型 workspace。

English: [README.md](./README.md)

Dev Skills 提供一种接近 Trellis 的开发体验，但不替代项目自己的文档体系：
从一个入口开始，澄清需求，打开基于 ADR / workstream 的执行通道，拆分垂直任务，
执行实现或诊断循环，review 已完成切片，用新鲜证据验证结果，并为后续会话和多 agent 留下可追溯记录。

## 使用体验

大多数时候，从一个 prompt 开始：

```text
使用 $dev-flow 处理这个 Rust 项目。
```

如果仓库陌生、已有旧版 workstream 文档，或者你不确定是否需要多终端，先做项目规模审计：

```text
使用 $audit-project-scale 审计这个 Rust 仓库，并选择合适的 dev-skills 路径。
```

如果输入仍然是宽泛产品愿景，先塑造产品架构，再打开 workstream：

```text
使用 $shape-product-architecture 把这个产品目标整理成有边界的 vision、MVP ladder、
capability map、architecture lanes、ADR candidates 和初始 workstream 优先级。
```

大型项目可以把一个终端长期分配给一个架构域：

```text
使用 $run-architecture-lane 负责 storage lane。
```

`$dev-flow` 是总入口。用户描述意图，skill 决定是否初始化文档、澄清需求、打开或恢复
workstream、执行单个任务、诊断失败、审查架构、分配架构 lane 或准备 handoff。

大型项目里，用户通常保留一个上层架构终端，同时直接和各个 lane 终端聊天。上层终端定期审查
进度和集成风险；lane 终端在已批准边界内持续深化自己的子架构。

内部路由大致如下：

```text
audit-project-scale -> dev-flow -> grill-with-docs/shape-product-architecture/plan-engineering-program/plan-architecture-lane -> open-workstream/run-architecture-lane -> integrate-lane-results/review-workstream/verify-rust-workstream -> close-workstream/handoff
```

日常开发中，用户不需要手动调用 `plan-architecture-lane`、`open-workstream`、`resume-workstream`、
`run-workstream-task`、`review-workstream`、`verify-rust-workstream` 或 `close-workstream`。
这些是 `$dev-flow`、`$plan-engineering-program`、`$run-architecture-lane` 或
`$integrate-lane-results` 根据项目状态自动选择的工作流动作。

当下一步有歧义时，agent 应该说明当前阶段、推荐路线、原因、现在可以做的只读动作、哪些 side
effects 需要批准，以及用户接下来应该使用的准确 prompt 或产物路径。

## 开发模型

这套流程面向聊天记录不可靠的大项目。

```text
product docs -> ADR -> workstream -> task ledger -> journal/handoff -> chat
```

- **Product docs**：产品意图、参考产品压力、MVP 阶段、client surfaces、non-goals、
  capability map 和优先级。
- **ADR**：长期架构契约和难以回滚的决策。
- **Workstream**：一个持久工程通道，包含设计、里程碑、证据、验证门槛和收尾。
- **Task ledger**：`TODO.md` 中的多 agent 任务账本，记录 owner、scope、依赖、验证和 handoff。
- **Journal / handoff**：会话连续性记录，但不能高于 ADR 或 workstream 文档。

上层架构 planner 负责创建或复用 workstream、维护 task ledger、生成 lane goal bundle 和全局顺序。
Lane / worker 终端负责实现分配的 bundle 或 task；可以提出同 lane 的下一个中型目标，但不重新定义全局计划。
创建 workstream 或 bundle 前，`$plan-engineering-program` 和 `$plan-architecture-lane` 选择 planning depth：
文档符合代码时轻量规划，任务边界需要代码证据时做 code-aware planning，lane seam 或 docs/code
对齐不清楚时先做架构审查。

对于大型系统，**architecture lane** 可以把一个终端 / worktree 长期绑定到某个能力域，
例如 storage、transcode、playback、realtime 或 admin。该终端连续推进同一能力域下的
workstream 队列，并显式标出需要跨 lane 协调的 shared scopes。

多 worktree 工作中，优先保持一个 architecture lane 一个长期 worktree，而不是每个
workstream 新建一个 worktree。上层 planner 负责提出终端/worktree 布局、分支名、创建命令和
提示词；用户批准后，上层 planner 可以帮忙创建，或把命令交给用户执行。Lane 终端完成任务后
推荐同 lane 下一步，但全局顺序仍由上层 planner 负责。

长期运行的终端应该先由上层 planner 准备 **lane goal bundle**：一个 lane、一个稳定 worktree、
一个 active workstream 或短的同 lane 队列、一到三个 ready tasks、owned/shared scopes、
validation commands、context manifest 和 stop conditions。Codex goal 适合这个 bundle、一个
有边界任务，或已批准的 lane campaign；不适合作为整个 architecture lane 的无限目标。
当 bundle、campaign 或 task 已经适合较长时间自动执行时，上层 planner 或 lane 输出应包含要设置的精确 Codex goal，
并询问是否设置，让 lane 终端一直执行到完成、阻塞或触发 stop condition。

如果某个 lane 要跨很多会话持续深化，不要把这个长期愿景塞进 Codex goal；把它放在 architecture
docs 或 lane roadmap 里：current state、target maturity、capability gaps、active/draft/deferred
workstreams、validation ladder、shared scopes 和 next bundles。队列变薄时，上层 planner 应该用
`$plan-architecture-lane`、source coverage audit，并在 docs/code 对齐不清楚时用 scoped
`$improve-codebase-architecture` 刷新 backlog。它也应该主动挖掘同 lane 的深化候选，而不是只消费
已有 TODO。如果已经有足够多的有序 bundles ready，上层 planner 可以批准 lane campaign，让 goal 按
gate 和 checkpoint 连续跑多个 bundle 后再请求输入。
分配 worker 或 lane 终端后，上层 planner 也可以用空档做只读 architecture reconnaissance：对全仓库或
单个 lane 做 scoped review、检查 docs/code drift、发现下一波候选任务。
当工作不适合并行但可以按顺序推进时，上层 planner 应该提出一个稳定 worktree 上的 serial lane
campaign，而不是不断给单任务 prompt。
Campaign 也可以携带明确的 side-effect policy，例如在已接受 bundle 边界自动 commit、把 main 同步回
lane worktree，或在新鲜 gates 通过后把已接受 lane slice merge 回 main。遇到冲突、失败 gates、
无关 dirty files、ADR/schema/public contract 变化、related-repo 决策或未批准 push 时仍然停止。

## 工作方法论

这套工作流组合了几个务实的软件工程方法：

- **DDD** 用于共享语言、ADR 和能力边界。
- **Team Topologies** 用于一个终端 / worktree 对应一个 stream-aligned architecture lane。
- **Shape Up** 用于中等大小 campaign，避免碎片 prompt 或无边界 goal。
- **Mikado Method** 用于重构前先拆依赖和 enabling moves。
- **Theory of Constraints** 用于按关键路径调度，而不是追求终端数量最大化。
- **XP/TDD 和 Continuous Delivery** 用于快速反馈、review、验证和频繁安全集成。

核心原则是 intent compression：用持久 lane docs、campaign、ADR 和 gates，让更短的 prompt
表达更准确的意图。用户精力是最贵的 token：agent 应该先花时间只读调查代码和文档，再给出有证据的建议；
只有产品方向、架构契约决策，或未被 campaign policy 预先批准的 side effects 才打断用户。

## 按仓库规模选择

使用能保护项目的最小工作流形态。

| 仓库情况 | 用户入口 | 预期形态 |
| --- | --- | --- |
| 宽泛产品目标、MVP 不清楚或参考产品野心较大 | `$shape-product-architecture` | Product vision、MVP ladder、capability map、lanes 和 ADR candidates |
| 小仓库、一个终端、一个有边界的 bug 或功能 | `$dev-flow` | 直接 `tdd` / `diagnose`，不一定需要 workstream |
| 中型仓库、多步骤功能或重构 | `$dev-flow` | 一个 workstream，带 task ledger 和 evidence gates |
| 大型仓库、有稳定能力域 | `$audit-project-scale`，再 `$plan-engineering-program` 和 `$run-architecture-lane` | 稳定 lane worktree，加已批准 campaign |
| 已经有多个终端在跑 | `$plan-engineering-program` / `$integrate-lane-results` | 上层规划后续 campaign；完成输出走集成 |
| 旧版或不清楚的 workstream / architecture 文档 | `$audit-project-scale` | 先修复工作流基底，再规划新工作 |

## 用户需要知道的本地 Skills

- [`dev-flow`](./skills/engineering/dev-flow/SKILL.md)：总入口和路由器。
- [`audit-project-scale`](./skills/engineering/audit-project-scale/SKILL.md)：审计仓库规模、现有文档和多终端可行性，
  决定走 direct task、workstream 还是 architecture lane。
- [`shape-product-architecture`](./skills/engineering/shape-product-architecture/SKILL.md)：把宽泛产品愿景转成
  product docs、MVP 阶段、capability map、lane 优先级和 ADR candidates。
- [`run-architecture-lane`](./skills/engineering/run-architecture-lane/SKILL.md)：让一个终端长期
  负责大型架构域，并连续推进该架构域下的 workstream 队列。
- [`plan-engineering-program`](./skills/engineering/plan-engineering-program/SKILL.md)：规划上层工程 program、lane roadmap、campaign 和多终端布局。
- [`integrate-lane-results`](./skills/engineering/integrate-lane-results/SKILL.md)：检查已完成 lane / worker 输出，路由 review、verify、commit、merge、sync 和下一步。
- [`codex-session-recovery`](./skills/engineering/codex-session-recovery/SKILL.md)：在 Codex
  会话崩溃、上下文损坏或 encrypted-content 失败后，手动从 session JSONL 恢复连续性线索。

大多数用户只需要理解这些入口。其余本地 skills 是内部工作流步骤，应由 `$dev-flow`、
`$run-architecture-lane`、`$plan-engineering-program` 或 `$integrate-lane-results` 调用。

## 内部本地 Workflow Skills

- [`setup-rust-workstreams`](./skills/engineering/setup-rust-workstreams/SKILL.md)：初始化 Rust 项目的工作流文档。
- [`fearless-refactor`](./skills/engineering/fearless-refactor/SKILL.md)：把架构审查发现转成由
  dev-flow 承接的 Rust 无畏重构执行通道。
- [`open-workstream`](./skills/engineering/open-workstream/SKILL.md)：创建或复用 durable workstream。
- [`plan-architecture-lane`](./skills/engineering/plan-architecture-lane/SKILL.md)：把选定子架构方向转成 workstream、worktree 和 lane bundle 计划。
- [`run-workstream-task`](./skills/engineering/run-workstream-task/SKILL.md)：执行 `TODO.md` 中的一个任务。
- [`review-workstream`](./skills/engineering/review-workstream/SKILL.md)：按 workstream contract 和代码质量 review worker 产出。
- [`verify-rust-workstream`](./skills/engineering/verify-rust-workstream/SKILL.md)：在任务、goal 或 lane 完成前运行新鲜 Rust 验证门槛。
- [`resume-workstream`](./skills/engineering/resume-workstream/SKILL.md)：从项目文档恢复状态。
- [`close-workstream`](./skills/engineering/close-workstream/SKILL.md)：收尾 evidence、gates、status 和 follow-ons。
- [`changelog`](./skills/engineering/changelog/SKILL.md)：根据 git 历史维护符合 Keep a Changelog
  风格的 `CHANGELOG.md`。
- [`commit-work`](./skills/engineering/commit-work/SKILL.md)：在检查和精准 stage 后创建安全、
  聚焦的 Conventional Commits。

## Misc Skills

Misc skills 对 Codex 有帮助，但不属于默认 Rust 工程工作流。它们只有在显式请求时才会安装。

- [`humanizer`](./skills/misc/humanizer/SKILL.md)：移除文章里的 AI 写作痕迹，同时保留语义、事实、
  术语和作者原本语气。改编自 [`blader/humanizer`](https://github.com/blader/humanizer)。

## Matt Pocock Skills

来自 [`mattpocock/skills`](https://github.com/mattpocock/skills)：

- **默认流程依赖**：`grill-with-docs`、`tdd`、`diagnose`、`handoff`。
- **大型 Rust 项目推荐**：`zoom-out`、`improve-codebase-architecture`、`prototype`。
- **按需主动调用**：`setup-matt-pocock-skills`、`to-prd`、`to-issues`、`triage`、
  `write-a-skill`、`grill-me`、`caveman`。

Dev Skills 不 vendor 这些上游 skills，只和它们组合：planner skills 用 `zoom-out` 和
`improve-codebase-architecture` 做只读发现，执行阶段路由到 `tdd` 或 `diagnose`，文档和连续性路由到
`grill-with-docs` 和 `handoff`。

## 常用 Prompt

继续开发：

```text
使用 $dev-flow 继续这个 Rust 项目。
```

初始化仓库：

```text
使用 $dev-flow 为这个 Rust 仓库初始化 dev-skills 工作流。
```

审计已有或不确定规模的仓库：

```text
使用 $audit-project-scale 审计这个 Rust 仓库。判断它应该走直接 $dev-flow 任务、普通 workstream，还是带上层架构终端的 architecture lanes。
```

规划大功能：

```text
使用 $dev-flow 规划这个功能。如果需求还不清楚，先澄清需求；然后创建或复用合适的 workstream，并拆分可执行任务。
```

塑造产品架构：

```text
使用 $shape-product-architecture 把这个产品目标整理成有边界的 vision、MVP ladder、
capability map、architecture lanes、ADR candidates 和初始 workstream 优先级。
```

运行长期架构终端：

```text
使用 $run-architecture-lane 负责 nako 的 storage lane。
把已批准的 lane bundle 或 lane campaign 作为最大自主范围。
保持这个终端专注 storage/VFS workstreams；遇到数据库或 server 共享契约变更时停止并请求协调。
```

执行指定任务：

```text
使用 $dev-flow 执行 docs/workstreams/<slug>/TODO.md 里的任务 ABC-020。
```

多终端协调：

```text
使用 $plan-engineering-program 检查这个仓库，识别 active workstreams 或 architecture lanes，并推荐上层 planner、lane、worker、reviewer 和 docs 终端。
先输出 Program Action 的 Mode、Now 和 Why。
在需求、文档和 gates 清楚时，规划 lane goal bundles，或更深的 lane campaign。
证据支持时列出 3-5 个候选方向，但默认最多激活 3 个 lane / worker 终端。lane map 或模块边界不清楚时，用一个 planner/recon 终端或一个 serial campaign。
同时输出 WIP 数量、assignment go/no-go、autonomy horizon 和 integration bottleneck 风险。
当 active queue 变薄时，主动检查 code/docs 并提出同 lane 深化候选，不要等用户追问。
分配终端后，如果没有 pending integration/review 工作，继续做只读 architecture reconnaissance。
根据当前状态选择 Program Action mode：DISCOVERY、SHAPE、PLAN、ASSIGN、RECON 或 DECISION。
当任务有依赖顺序且不适合并行时，优先使用一个 serial lane campaign，不要开多个会被 BLOCKED 的终端，也不要反复让用户复制单任务 prompt。
对于 active 或 stale worktrees，先用 result-intake helper，不要先让我手动复制聊天。
优先一个 architecture lane 一个长期 worktree。用户批准建议的布局、命令、终端提示词和 side effects 前，不要创建 worktree 或分支。
写出每个已批准 task、bundle 或 campaign 要设置的精确 Codex goal。
```

结果集成：

```text
使用 $integrate-lane-results 检查已完成的 lane worktree，分类结果，安排 review/verify，并提出 fix、commit、merge、sync 或 next-campaign 动作。
```

使用 Codex goal：

```text
把 docs/workstreams/<slug>/TODO.md 里的任务 ABC-020 设置为当前 Codex goal。只有在验证通过并更新 task ledger 后，才标记 goal 完成。
```

给已批准的 lane bundle 设置 Codex goal：

```text
把 planner state 里的 lane bundle storage-20260530-01 设置为当前 Codex goal。
保持在 bundle scope 内；遇到 shared-scope 变更或缺失 context 时停止，并回报上层 planner / integrator。
```

给已批准的 lane campaign 设置 Codex goal：

```text
把 planner state 里的 lane campaign storage-20260531-01 设置为当前 Codex goal。
只有每一步 gate 通过时才自动推进下一个 bundle；遇到 shared scopes、ADR/schema/contract 变更、失败 gate、缺失 context 或未批准 side effects 时停止。
```

review 并验证任务：

```text
使用 $dev-flow review 并验证任务 ABC-020，然后再标记完成。
```

恢复异常 Codex 会话：

```text
使用 $codex-session-recovery 从 latest Codex session 恢复上下文。
```

## Rust 模拟器项目示例

```text
使用 $dev-flow 启动一个新的 Rust homebrew-first emulator/simulator 项目。
如果缺少工作流文档，先初始化；然后澄清 MVP、法律/范围边界，提出第一批架构决策，再打开第一个 durable workstream。
在第一个验证门槛明确前，不要开始大范围实现。
```

## 安装

默认安装本地 required skills 和最小 upstream 依赖：

```powershell
python .\scripts\install_dev_skills.py
```

推荐安装集，包含 session 恢复、changelog 维护、commit 创建和无畏重构 skill：

```powershell
python .\scripts\install_dev_skills.py --include-recommended
```

完整安装集：

```powershell
python .\scripts\install_dev_skills.py --include-recommended --include-optional
```

安装 misc skills，例如写作辅助：

```powershell
python .\scripts\install_dev_skills.py --include-misc
```

安装或更新后重启 Codex。

更多文档：

- [中文使用说明](./docs/zh-CN/usage.md)
- [中文安装说明](./docs/zh-CN/install.md)
- [中文工作流](./docs/zh-CN/workflow.md)
- [大型 Rust 工作流行为评测](./docs/evals/large-rust-workflow.md)
- [中文多终端 Playbook](./docs/zh-CN/playbooks/multi-terminal-development.md)
- [中文设计原则](./docs/zh-CN/design-principles.md)

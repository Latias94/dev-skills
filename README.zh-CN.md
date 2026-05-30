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

大型项目可以把一个终端长期分配给一个架构域：

```text
使用 $run-architecture-lane 负责 storage lane。
```

`$dev-flow` 是总入口。用户描述意图，skill 决定是否初始化文档、澄清需求、打开或恢复
workstream、执行单个任务、诊断失败、审查架构、分配架构 lane 或准备 handoff。

内部路由大致如下：

```text
audit-project-scale -> dev-flow -> grill-with-docs -> open-workstream/run-architecture-lane -> run-workstream-task -> review-workstream -> verify-rust-workstream -> close-workstream/handoff
```

日常开发中，用户不需要手动调用 `open-workstream`、`resume-workstream`、
`run-workstream-task`、`review-workstream`、`verify-rust-workstream` 或 `close-workstream`。
这些是 `$dev-flow` 根据项目状态自动选择的工作流动作。

## 开发模型

这套流程面向聊天记录不可靠的大项目。

```text
ADR -> workstream -> task ledger -> journal/handoff -> chat
```

- **ADR**：长期架构契约和难以回滚的决策。
- **Workstream**：一个持久工程通道，包含设计、里程碑、证据、验证门槛和收尾。
- **Task ledger**：`TODO.md` 中的多 agent 任务账本，记录 owner、scope、依赖、验证和 handoff。
- **Journal / handoff**：会话连续性记录，但不能高于 ADR 或 workstream 文档。

对于大型系统，**architecture lane** 可以把一个终端 / worktree 长期绑定到某个能力域，
例如 storage、transcode、playback、realtime 或 admin。该终端连续推进同一能力域下的
workstream 队列，并显式标出需要跨 lane 协调的 shared scopes。

## 按仓库规模选择

使用能保护项目的最小工作流形态。

| 仓库情况 | 用户入口 | 预期形态 |
| --- | --- | --- |
| 小仓库、一个终端、一个有边界的 bug 或功能 | `$dev-flow` | 直接 `tdd` / `diagnose`，不一定需要 workstream |
| 中型仓库、多步骤功能或重构 | `$dev-flow` | 一个 workstream，带 task ledger 和 evidence gates |
| 大型仓库、有稳定能力域 | `$audit-project-scale`，再 `$run-architecture-lane` | 每个能力域一个 lane 终端，加 planner 协调 |
| 已经有多个终端在跑 | `$coordinate-workstream` | planner 集成 lane / worker / reviewer 产出 |
| 旧版或不清楚的 workstream / architecture 文档 | `$audit-project-scale` | 先修复工作流基底，再规划新工作 |

## 用户需要知道的本地 Skills

- [`dev-flow`](./skills/engineering/dev-flow/SKILL.md)：总入口和路由器。
- [`audit-project-scale`](./skills/engineering/audit-project-scale/SKILL.md)：审计仓库规模、现有文档和多终端可行性，
  决定走 direct task、workstream 还是 architecture lane。
- [`run-architecture-lane`](./skills/engineering/run-architecture-lane/SKILL.md)：让一个终端长期
  负责大型架构域，并连续推进该架构域下的 workstream 队列。
- [`coordinate-workstream`](./skills/engineering/coordinate-workstream/SKILL.md)：协调 planner、lane、worker、reviewer 和 docs 终端。
- [`codex-session-recovery`](./skills/engineering/codex-session-recovery/SKILL.md)：在 Codex
  会话崩溃、上下文损坏或 encrypted-content 失败后，手动从 session JSONL 恢复连续性线索。

大多数用户只需要理解这些入口。其余本地 skills 是内部工作流步骤，应由 `$dev-flow`、
`$run-architecture-lane` 或 `$coordinate-workstream` 调用。

## 内部本地 Workflow Skills

- [`setup-rust-workstreams`](./skills/engineering/setup-rust-workstreams/SKILL.md)：初始化 Rust 项目的工作流文档。
- [`fearless-refactor`](./skills/engineering/fearless-refactor/SKILL.md)：把架构审查发现转成由
  dev-flow 承接的 Rust 无畏重构执行通道。
- [`open-workstream`](./skills/engineering/open-workstream/SKILL.md)：创建或复用 durable workstream。
- [`run-workstream-task`](./skills/engineering/run-workstream-task/SKILL.md)：执行 `TODO.md` 中的一个任务。
- [`review-workstream`](./skills/engineering/review-workstream/SKILL.md)：按 workstream contract 和代码质量 review worker 产出。
- [`verify-rust-workstream`](./skills/engineering/verify-rust-workstream/SKILL.md)：在任务、goal 或 lane 完成前运行新鲜 Rust 验证门槛。
- [`resume-workstream`](./skills/engineering/resume-workstream/SKILL.md)：从项目文档恢复状态。
- [`close-workstream`](./skills/engineering/close-workstream/SKILL.md)：收尾 evidence、gates、status 和 follow-ons。
- [`changelog`](./skills/engineering/changelog/SKILL.md)：根据 git 历史维护符合 Keep a Changelog
  风格的 `CHANGELOG.md`。

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
使用 $audit-project-scale 审计这个 Rust 仓库。判断它应该走直接 $dev-flow 任务、普通 workstream，还是带 planner 终端的 architecture lanes。
```

规划大功能：

```text
使用 $dev-flow 规划这个功能。如果需求还不清楚，先澄清需求；然后创建或复用合适的 workstream，并拆分可执行任务。
```

运行长期架构终端：

```text
使用 $run-architecture-lane 负责 nako 的 storage lane。保持这个终端专注 storage/VFS workstreams；遇到数据库或 server 共享契约变更时停止并请求协调。
```

执行指定任务：

```text
使用 $dev-flow 执行 docs/workstreams/<slug>/TODO.md 里的任务 ABC-020。
```

多终端协调：

```text
使用 $coordinate-workstream 检查这个仓库，识别 active workstreams 或 architecture lanes，并推荐 planner、lane、worker、reviewer 和 docs 终端。
```

使用 Codex goal：

```text
把 docs/workstreams/<slug>/TODO.md 里的任务 ABC-020 设置为当前 Codex goal。只有在验证通过并更新 task ledger 后，才标记 goal 完成。
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

推荐安装集，包含 session 恢复、changelog 维护和无畏重构 skill：

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
- [中文多终端 Playbook](./docs/zh-CN/playbooks/multi-terminal-development.md)
- [中文设计原则](./docs/zh-CN/design-principles.md)

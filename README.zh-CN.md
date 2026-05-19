# Dev Skills

面向大型 Rust 项目的可复用 Codex skills。

English: [README.md](./README.md)

Dev Skills 提供一种接近 Trellis 的开发体验，但不替代项目自己的文档体系：
从一个入口开始，澄清需求，打开基于 ADR / workstream 的执行通道，拆分垂直任务，
执行实现或诊断循环，review 已完成切片，用新鲜证据验证结果，并为后续会话和多 agent 留下可追溯记录。

## 使用体验

大多数时候，从一个 prompt 开始：

```text
使用 $dev-flow 处理这个 Rust 项目。
```

`$dev-flow` 是总入口。用户描述意图，skill 决定是否初始化文档、澄清需求、打开或恢复
workstream、执行单个任务、诊断失败、审查架构或准备 handoff。

内部路由大致如下：

```text
dev-flow -> grill-with-docs -> open-workstream -> coordinate-workstream -> run-workstream-task -> review-workstream -> verify-rust-workstream -> close-workstream/handoff
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

## 本地 Skills

- [`dev-flow`](./skills/engineering/dev-flow/SKILL.md)：总入口和路由器。
- [`setup-rust-workstreams`](./skills/engineering/setup-rust-workstreams/SKILL.md)：初始化 Rust 项目的工作流文档。
- [`open-workstream`](./skills/engineering/open-workstream/SKILL.md)：创建或复用 durable workstream。
- [`coordinate-workstream`](./skills/engineering/coordinate-workstream/SKILL.md)：协调 planner、worker、reviewer 和 docs 终端。
- [`run-workstream-task`](./skills/engineering/run-workstream-task/SKILL.md)：执行 `TODO.md` 中的一个任务。
- [`review-workstream`](./skills/engineering/review-workstream/SKILL.md)：按 workstream contract 和代码质量 review worker 产出。
- [`verify-rust-workstream`](./skills/engineering/verify-rust-workstream/SKILL.md)：在任务、goal 或 lane 完成前运行新鲜 Rust 验证门槛。
- [`resume-workstream`](./skills/engineering/resume-workstream/SKILL.md)：从项目文档恢复状态。
- [`close-workstream`](./skills/engineering/close-workstream/SKILL.md)：收尾 evidence、gates、status 和 follow-ons。
- [`codex-session-recovery`](./skills/engineering/codex-session-recovery/SKILL.md)：在 Codex
  会话崩溃、上下文损坏或 encrypted-content 失败后，手动从 session JSONL 恢复连续性线索。

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

规划大功能：

```text
使用 $dev-flow 规划这个功能。如果需求还不清楚，先澄清需求；然后创建或复用合适的 workstream，并拆分可执行任务。
```

执行指定任务：

```text
使用 $dev-flow 执行 docs/workstreams/<slug>/TODO.md 里的任务 ABC-020。
```

多终端协调：

```text
使用 $coordinate-workstream 协调当前 workstream，覆盖 planner、worker、reviewer 和 docs 终端。
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

推荐安装集，包含手动 session 恢复 skill：

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

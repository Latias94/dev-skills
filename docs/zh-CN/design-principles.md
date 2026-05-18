# 设计原则

English: [../design-principles.md](../design-principles.md)

这个仓库结合四类影响：

1. Trellis 风格的开发体验
2. `mattpocock/skills` 风格的 skill 设计
3. Superpowers 风格的 review / verification hard gates
4. 大型 Rust 项目的治理方式：ADR、workstream、evidence gates 和严格 git safety

## 从 Trellis 借鉴什么

Trellis 的价值主要在执行体验：

- 清晰的开发入口
- 执行前规划
- 以任务为中心的 agent 工作
- session journal 用于跨会话连续性
- planner / worker / reviewer 等多角色

我们采用这些作为 workflow pattern。

## 不从 Trellis 借鉴什么

我们不让 Trellis-like artifacts 变成第二套事实源。

- 不创建和 ADR 竞争的第二套架构规格。
- 不创建和 workstream `TODO.md` 竞争的任务系统。
- 不允许 journal-only 决策。
- 不允许自动 harness 在未经 review 的情况下改写仓库规则。

对大型 Rust 项目，项目自己的文档保持权威。

## 从 mattpocock/skills 借鉴什么

skill 设计遵循小而可组合：

- 每个 skill 只做一件窄任务。
- frontmatter description 清楚说明何时使用。
- `SKILL.md` 保持精简。
- 细节放到 `references/`。
- 可复用模板放到 `assets/`。
- 组合上游 skills，而不是复制它们。

## 从 Superpowers 借鉴什么

Superpowers 的价值在流程 gate：

- 完成的工作先 review，再接受。
- review 分开看“是否满足 spec”和“代码质量是否过关”。
- 声称完成前必须有新鲜验证证据。
- worker 用明确状态汇报，而不是笼统说“完成了”。
- 分支或 workstream 收尾是一个决策点，不是自然消失。

这个仓库吸收这些 gate，但不采用 Superpowers 的全局 bootstrap 或强制自动触发策略。

## 我们自己的层

自定义层面向大型 Rust 项目：

- ADR 高于 workstream。
- Workstream 是持久工程通道。
- `TODO.md` 是多 agent task ledger。
- `EVIDENCE_AND_GATES.md` 记录验证证据，而不只是命令。
- `WORKSTREAM.json` 给 agent 快速读取状态。
- `JOURNAL/` 和 `HANDOFF.md` 支持会话连续性，但不定义事实。
- Rust 验证优先 `cargo nextest run`。
- Git safety 和保留用户变更是硬要求。

## 最终形态

```text
Trellis inspiration: session flow, task focus, multi-agent roles
mattpocock inspiration: small composable skills, progressive disclosure
Superpowers inspiration: hard review and verification gates
our workflow: ADR + workstream + task ledger + journal for large Rust projects
```

目标是 Trellis-like execution，而不是 Trellis-like source-of-truth duplication。

# 使用说明

English: [../usage.md](../usage.md)

大多数时候，从 `$dev-flow` 开始。

`$dev-flow` 是总入口。它应该主动委托给下一个合适的 skill，而不是只告诉用户下一步该用哪个 skill。

## 常用调用

初始化项目：

```text
使用 $dev-flow 为这个 Rust 仓库初始化 dev-skills 工作流。
```

规划大功能：

```text
使用 $dev-flow 规划这个功能。如果需求还不清楚，先澄清需求；然后创建或复用合适的
workstream，并拆分可执行任务。
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

协调多终端：

```text
使用 $coordinate-workstream 协调当前 workstream，覆盖 planner、worker、reviewer 和 docs 终端。
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

## Codex Goals

Codex goal 适合绑定到 workstream task ledger 里的一个具体任务。

适合：

- `TODO.md` 里的一个 task ID
- 一个单独 bug fix
- 一个有边界的验证循环

不适合：

- 整个 workstream
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

## 内部工作流 Skills

这些通常由 `$dev-flow` 调用，不需要用户手动调用：

- `setup-rust-workstreams`
- `open-workstream`
- `coordinate-workstream`
- `resume-workstream`
- `run-workstream-task`
- `review-workstream`
- `verify-rust-workstream`
- `close-workstream`

只有在你明确要绕过路由器，或 planner 终端正在多终端协调时，才直接调用它们。

## 多 Agent 使用

只有当任务边界清楚时才并行。

Planner prompt：

```text
使用 $coordinate-workstream 为当前 workstream 准备并行工作。
只有在 owner、范围、依赖关系和验证命令都明确时，才分配任务。
```

Worker prompt：

```text
使用 $run-workstream-task 执行任务 ABC-020。它应该按需委托给 $tdd 或 $diagnose，
保持在分配的文件范围内，并在完成后更新 task ledger 和 journal。
```

Reviewer prompt：

```text
使用 $review-workstream 根据 workstream contract 和仓库标准 review 已完成任务 ABC-020。
```

Verifier prompt：

```text
使用 $verify-rust-workstream 用新鲜命令证据验证任务 ABC-020，然后再标记完成。
```

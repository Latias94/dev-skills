# Usage

中文文档: [zh-CN/usage.md](./zh-CN/usage.md)

Most users should start with `$dev-flow`.

`$dev-flow` is the orchestrator. It should actively delegate to the next skill instead of only
telling the user what to do next.

## Common User Calls

Initialize a project:

```text
使用 $dev-flow 为这个 Rust 仓库初始化 dev-skills 工作流。
```

Plan a large feature:

```text
使用 $dev-flow 规划这个功能。如果需求还不清楚，先澄清需求；然后创建或复用合适的
workstream，并拆分可执行任务。
```

Implement a bounded task:

```text
使用 $dev-flow 执行 docs/workstreams/<slug>/TODO.md 里的任务 ABC-020。
```

Debug a failure:

```text
使用 $dev-flow 诊断这个失败测试，并把回归证据记录到当前 workstream。
```

Prepare a handoff:

```text
使用 $dev-flow 为当前 workstream 准备 handoff。
```

Coordinate multiple terminals:

```text
使用 $coordinate-workstream 协调当前 workstream，覆盖 planner、worker、reviewer 和 docs 终端。
```

## Direct Matt Pocock Skill Calls

Call these directly when you want that explicit action, rather than the normal development router.

Configure issue tracker/domain docs:

```text
使用 $setup-matt-pocock-skills 为这个仓库配置 AGENTS.md 和 docs/agents。
```

Pressure-test an idea before project docs exist:

```text
使用 $grill-me 拷问这个项目想法，直到 MVP、非目标和风险都足够明确。
```

Pressure-test a plan against existing docs:

```text
使用 $grill-with-docs 根据 CONTEXT.md、ADR 和当前 workstream 压力测试这个方案。
```

Understand unfamiliar code:

```text
使用 $zoom-out 解释这个子系统如何融入整个项目。
```

Review architecture:

```text
使用 $improve-codebase-architecture 查找 crate 边界、模块深度和可测试性问题。
```

Build a throwaway experiment:

```text
使用 $prototype 在写入 ADR 前测试两种设计。
```

Export to project tracker:

```text
使用 $to-prd 把这个已澄清方案整理成 PRD；如果需要进入 GitHub Issues，再使用 $to-issues。
```

Create a reusable skill:

```text
使用 $write-a-skill 为这个重复工作流创建一个项目专属 skill。
```

## Default User Experience

```text
User -> $dev-flow -> delegated skill -> $dev-flow resumes routing
```

The user should not need to remember internal workflow skills. `$dev-flow` should decide whether the
next move is bootstrap, grill, workstream planning, TDD execution, diagnosis, review, or handoff.

Example chain:

```text
User asks for large feature
-> $dev-flow detects unclear requirements
-> delegates to $grill-with-docs
-> resumes and delegates to $open-workstream
-> creates task ledger
-> delegates multi-terminal planning to $coordinate-workstream when needed
-> delegates first task to $tdd or $diagnose
-> records evidence and handoff
```

## Codex Goals

Codex goals are useful for one bounded task from a workstream task ledger.

Use goals for:

- one task ID from `TODO.md`,
- a single bug fix,
- a bounded validation loop.

Do not use goals for:

- the whole workstream,
- long-term architecture memory,
- replacing ADRs or workstream docs.

Recommended pattern:

```text
1. $open-workstream creates task ABC-020.
2. User asks Codex to set ABC-020 as the current goal.
3. Agent executes and validates the task.
4. Agent marks the goal complete only after the task is genuinely done.
5. Agent updates TODO.md and EVIDENCE_AND_GATES.md.
```

## Internal Workflow Skills

These are normally invoked by `$dev-flow`, not manually:

- `setup-rust-workstreams`
- `open-workstream`
- `coordinate-workstream`
- `resume-workstream`
- `run-workstream-task`
- `close-workstream`

Directly call one only when you intentionally want to bypass the router, or when the planner terminal
is actively coordinating multiple terminals with `coordinate-workstream`.

## Multi-Agent Use

Only parallelize when tasks have clear boundaries.

Planner prompt:

```text
使用 $coordinate-workstream 为当前 workstream 准备并行工作。
只有在 owner、范围、依赖关系和验证命令都明确时，才分配任务。
```

Worker prompt:

```text
使用 $run-workstream-task 执行任务 ABC-020。它应该按需委托给 $tdd 或 $diagnose，
保持在分配的文件范围内，并在完成后更新 task ledger 和 journal。
```

Reviewer prompt:

```text
根据 workstream contract 和仓库标准 review 已完成任务。
```

Workers should not rewrite the global task ledger or redefine the workstream target state.

## Skill Delegation

When a skill hands off to another skill, it should pass the minimum durable context:

- workstream path,
- task ID,
- file scope,
- validation command,
- relevant ADR/docs,
- and expected output artifact.

Example:

```text
委托给 $tdd:
任务: ABC-020
Workstream: docs/workstreams/<slug>
范围: crates/foo/src/**
验证: cargo nextest run -p foo abc_020
期望输出: 代码变更、验证通过、TODO.md 状态更新、evidence note
```

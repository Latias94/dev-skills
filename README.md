# Dev Skills

Reusable Codex skills for large Rust projects.

中文文档: [README.zh-CN.md](./README.zh-CN.md)

Dev Skills gives you a Trellis-like development experience without replacing your project docs:
start from one entrypoint, clarify requirements, open an ADR/workstream-backed execution lane, split
vertical tasks, run implementation or diagnosis loops, and leave a traceable record for future
sessions and agents.

## Experience

Most users start with one prompt:

```text
使用 $dev-flow 处理这个 Rust 项目。
```

`$dev-flow` acts as an orchestrator. Users describe intent; the skill decides whether to initialize
docs, clarify requirements, open or resume a workstream, run a bounded task, diagnose a failure,
review architecture, or prepare a handoff.

Internal routing looks like this:

```text
dev-flow -> grill-with-docs -> open-workstream -> coordinate-workstream -> run-workstream-task -> close-workstream/handoff
```

Users should not need to manually call `open-workstream`, `resume-workstream`,
`run-workstream-task`, or `close-workstream` during ordinary development. Those are workflow actions
that `$dev-flow` should invoke when the project state calls for them.

## Development Model

The workflow is built for large projects where chat history is not a reliable source of truth.

```text
ADR -> workstream -> task ledger -> journal/handoff -> chat
```

- **ADR** records long-term architecture contracts and hard-to-change decisions.
- **Workstream** records a durable engineering lane: design, milestones, evidence, gates, and
  closeout.
- **Task ledger** records multi-agent slices in `TODO.md` with owner, scope, dependencies,
  validation, and handoff notes.
- **Journal / handoff** records session state for continuity, but never outranks ADRs or
  workstream docs.

This makes each task traceable: why it exists, which contract it follows, which worker owned it,
which files changed, and which gates prove it.

## Failure Modes This Fixes

Dev Skills is a set of small workflow skills, not a full project-management framework.

- **Agent starts coding too early** -> `$dev-flow` routes risky requirements to
  `$grill-with-docs`.
- **Big Rust changes lose the thread** -> `$open-workstream` creates durable docs and a task
  ledger.
- **New sessions do not know what happened** -> `$resume-workstream` reads `WORKSTREAM.json`,
  `TODO.md`, `HANDOFF.md`, journal, and git state.
- **Multiple agents collide** -> `TODO.md` records owner, scope, dependencies, and validation per
  task.
- **A worker tries to do everything** -> `$run-workstream-task` owns exactly one task.
- **The lane never closes** -> `$close-workstream` finalizes evidence, gates, status, and follow-ons.

## Skills

### Local Skills

- [`dev-flow`](./skills/engineering/dev-flow/SKILL.md) — orchestrates the whole development flow
  and delegates to the right skill.
- [`setup-rust-workstreams`](./skills/engineering/setup-rust-workstreams/SKILL.md) — initializes a
  Rust repo with Codex-friendly workflow docs, workstream conventions, and multi-agent guardrails.
- [`open-workstream`](./skills/engineering/open-workstream/SKILL.md) — creates or reuses a durable
  lane and writes the workstream artifact set.
- [`coordinate-workstream`](./skills/engineering/coordinate-workstream/SKILL.md) — coordinates
  planner, worker, reviewer, and docs terminals for one active workstream.
- [`run-workstream-task`](./skills/engineering/run-workstream-task/SKILL.md) — executes one task
  from `TODO.md` and delegates to `tdd` or `diagnose`.
- [`resume-workstream`](./skills/engineering/resume-workstream/SKILL.md) — reconstructs state from
  `WORKSTREAM.json`, `TODO.md`, `HANDOFF.md`, journal, and git state.
- [`close-workstream`](./skills/engineering/close-workstream/SKILL.md) — finalizes evidence, gates,
  status, and follow-ons.

### Upstream Skills Used By This Workflow

These come from [`mattpocock/skills`](https://github.com/mattpocock/skills):

- **Required by the flow**: `grill-with-docs`, `tdd`, `diagnose`, `handoff`.
- **Recommended for large Rust projects**: `zoom-out`, `improve-codebase-architecture`, `prototype`.
- **Direct, situational calls**: `setup-matt-pocock-skills`, `to-prd`, `to-issues`, `triage`,
  `write-a-skill`, `grill-me`, `caveman`.

Dev Skills does not vendor those upstream skills. It composes with them.

## User-Facing Prompts

Most daily work should start with intent, not an internal workflow step.

Start or continue normal development:

```text
使用 $dev-flow 继续这个 Rust 项目。
```

Initialize a repo:

```text
使用 $dev-flow 为这个 Rust 仓库初始化 dev-skills 工作流。
```

Plan a large feature:

```text
使用 $dev-flow 规划这个功能。如果需求还不清楚，先澄清需求；然后创建或复用合适的 workstream，并拆分可执行任务。
```

Execute a known task:

```text
使用 $dev-flow 执行 docs/workstreams/<slug>/TODO.md 里的任务 ABC-020。
```

Debug a failure:

```text
使用 $dev-flow 调试这个失败测试，并把回归证据记录到当前 workstream。
```

Prepare a handoff:

```text
使用 $dev-flow 为当前 workstream 准备 handoff。
```

## When To Call Other Skills Directly

Some skills are explicit user actions. Call them directly when that is the thing you want done.

Recommended upstream skills for your kind of work:

```text
当我需要系统级理解陌生代码时，使用 $zoom-out。
当已有一些代码、需要结构性审查时，使用 $improve-codebase-architecture。
当我想在确定设计前做一次可丢弃实验时，使用 $prototype。
```

Configure Matt Pocock issue-tracker/domain-doc assumptions:

```text
使用 $setup-matt-pocock-skills 为这个仓库配置 AGENTS.md 和 docs/agents。
```

Stress-test an idea before it becomes project docs:

```text
使用 $grill-me 拷问这个项目想法，直到 MVP、非目标和风险都足够明确。
```

Build a throwaway experiment:

```text
使用 $prototype 测试两种可能的执行循环设计，在确定架构前先验证思路。
```

Export to tracker artifacts:

```text
使用 $to-prd 把已经澄清的方案整理成 PRD；如果需要进入 GitHub Issues，再使用 $to-issues。
```

Create a new reusable workflow skill:

```text
使用 $write-a-skill 创建一个 emulator-trace-debug skill，用于调试 trace divergence。
```

Use Codex goals for one bounded task:

```text
把 docs/workstreams/<slug>/TODO.md 里的任务 ABC-020 设置为当前 Codex goal。只有在验证通过并更新 task ledger 后，才标记 goal 完成。
```

## Example: Rust Emulator Project

Day 0, start from a new idea:

```text
使用 $dev-flow 启动一个新的 Rust homebrew-first emulator/simulator 项目。
如果缺少工作流文档，先初始化；然后澄清 MVP、法律/范围边界，提出第一批架构决策，再打开第一个 durable workstream。
在第一个验证门槛明确前，不要开始大范围实现。
```

Early architecture experiment:

```text
使用 $prototype 比较这个 emulator 的 memory-bus 和 execution-trace 设计。
保持原型可丢弃。最后总结哪些结论应该沉淀为 ADR 材料。
```

Normal workday:

```text
使用 $dev-flow 继续这个 emulator 项目。
读取当前 workstream 状态，选择下一个安全任务，带测试执行，并更新 evidence。
```

Multi-agent planning:

```text
使用 $dev-flow 为当前 emulator workstream 准备并行工作。
只有在 owner、文件范围、依赖关系和验证命令都明确时，才拆分任务。
```

Planner / PM terminal:

```text
使用 $coordinate-workstream 协调当前 emulator workstream，覆盖 planner、worker、
reviewer 和 next-version docs 终端。
```

Debugging:

```text
使用 $dev-flow 诊断当前 emulator 任务里的 trace divergence。
构建确定性复现，修复问题，添加回归测试，并更新 evidence gate。
```

## Install

Default install copies local required skills and the minimal upstream dependencies:

```powershell
python .\scripts\install_dev_skills.py
```

PowerShell equivalent:

```powershell
.\scripts\install-dev-skills.ps1
```

Recommended upstream skills:

```powershell
python .\scripts\install_dev_skills.py --include-recommended
```

Restart Codex after installing or updating skills.

See [`docs/install.md`](./docs/install.md) for install sets and options.

Validate local skill authoring rules:

```powershell
python .\scripts\validate_skills.py
```

## Diagrams And Details

- [`docs/workflow.md`](./docs/workflow.md) — skill routing, artifact authority, and multi-agent
  execution diagrams.
- [`docs/usage.md`](./docs/usage.md) — user calls, Codex goals, and multi-agent usage.
- [`docs/playbooks/multi-terminal-development.md`](./docs/playbooks/multi-terminal-development.md)
  — planner, worker, reviewer, and docs terminal prompts.
- [`docs/design-principles.md`](./docs/design-principles.md) — how this borrows from Trellis and
  `mattpocock/skills`.

## Influences

- [`mattpocock/skills`](https://github.com/mattpocock/skills): small, composable skills with clear
  trigger descriptions, concise bodies, references, and assets.
- [`Trellis`](https://github.com/mindfold-ai/Trellis): task-centered development experience,
  planner/worker/reviewer roles, session continuity, and explicit execution flow.

Dev Skills adopts those ideas while keeping project-owned ADRs and workstreams as the authority.

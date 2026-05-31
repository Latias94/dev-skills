# 多终端开发

English: [../../playbooks/multi-terminal-development.md](../../playbooks/multi-terminal-development.md)

当一个 workstream 需要多个 Codex 终端，或大型项目采用每个架构域一个终端时，使用这个 playbook。

如果你不确定仓库是否需要这种协调强度，先运行 `$audit-project-scale`；小型或中型工作继续用
`$dev-flow`。

## 终端分工

```text
终端 1：上层架构 planner / commander
终端 2：Architecture lane A
终端 3：Architecture lane B
终端 4：Worker 或 diagnosis sidecar
终端 5：Reviewer / verifier / integrator
终端 6：Docs / next-wave planning
```

上层架构 planner 可以是一个单独终端，也可以是你的主控终端。它负责 workstream 创建/复用、
lane roadmap、全局顺序、shared-scope 决策和 task ledger 变更。Lane / worker 终端实现已批准
campaign、bundle 或 task，然后回报。
唯一角色契约以 `skills/engineering/dev-flow/references/multi-agent-flow.md` 为准；这个 playbook
只保留使用层面的说明。

对于 architecture lane 工作，上层 planner 负责跨 lane 优先级和 shared scopes。Lane 终端负责
storage、transcode、playback、realtime 或 admin 这类能力域。

上层 planner 回复应该以当前终端视角组织：先说这个终端现在要做什么，再列出需要粘贴到其他终端的
prompt。如果当前终端要做 result inspection、review 或新鲜验证，就直接写出来，不要写成
“让 planner/reviewer 去接受”。

## 上层 Planner 状态

多 worktree 工作中，把运行态放在本地 `.codex/planner-state.local.json` 或
`docs/local/PLANNER_STATE.md`。记录 repo path、branch、head、dirty status、lane/workstream、
active task、lane goal bundle、context manifest、session refs、shared scopes、validation 和
related repositories。只提交示例和 lane 名称，不提交个人机器上的绝对路径。

`session_refs` 只作为恢复指针。上层 planner 决策应该来自 workstream 文档、终端报告、git
state 和新鲜验证，而不是原始聊天记录。

## 报告格式

上层 planner 输出应该按状态组织，而不是套一个固定模板。Program planning report 先写：

```text
Mode: DISCOVERY | PLANNING | ASSIGNMENT | RECON | DECISION
Now: 当前上层架构终端下一步做什么
Why: 一句话说明依据的 repo 证据
```

Integration report 先写：

```text
Mode: RESULT_INTAKE | REVIEW_VERIFY | INTEGRATION_SYNC | BLOCKED_DECISION
Now: 当前 integration 终端下一步做什么
Why: 一句话说明依据的 repo 证据
```

lane/worktree 状态用表格，architecture reconnaissance 候选用编号列表并包含 `Files / Problem /
Solution / Benefits`，终端提示词用 fenced prompt。默认不要用 HTML；只有用户明确要 durable
dashboard 或报告 artifact 时才用 HTML。
每次上层 planner 报告都要包含 `Minimal User Input Needed`；如果 repo 证据已经足够，就写 `None`。

## 用户注意力规则

不要在 repo 证据还能继续检查时问用户“下一个任务是什么”。先花 agent 时间只读检查 architecture
docs、workstreams、git state、代码路径、`zoom-out` 和 scoped `improve-codebase-architecture`。
只有未被 campaign policy 覆盖的 side effects、产品方向、ADR/schema/public-contract 决策、
related-repo 动作，或给出最佳建议后仍存在真实 tradeoff 时，才问用户。

## Planner 发现 Prompt

当你还不知道当前应该跑哪个 workstream 或 lane 时，用这个。

```text
使用 $plan-engineering-program 检查这个仓库，并推荐多终端计划。
不要假设已经存在 current workstream。
读取 docs/architecture/LANES.md、WORKSTREAM_LINKS.md、docs/workstreams/*/WORKSTREAM.json、
git status、git worktree list，以及文档中提到的相关仓库。
只有 durable scope 和 gates 清楚时，才创建或复用 workstream。
选定子架构方向时用 $plan-architecture-lane；它会选择 planning depth，并在 lane seams / docs/code 对齐不清楚时转到 scoped $improve-codebase-architecture。
陌生代码先用 $zoom-out；ready queue 太薄或长期 lane 深度不清楚时，用 scoped $improve-codebase-architecture。
汇报候选 active workstreams 或 lanes、建议的 lane goal bundles、批准后要设置的 Codex goals、
推荐终端、已有或建议创建的 worktree 路径、分支同步阻塞项、建议的创建命令、终端提示词、
context manifests，以及每个终端应该先跑的任务。用户批准前，不要创建新 worktree 或分支。
使用 Program Action mode DISCOVERY、PLANNING 或 ASSIGNMENT。
```

## 已知 Workstream Planning Prompt

当 workstream 路径已经明确时，用这个。

```text
使用 $plan-engineering-program 规划 docs/workstreams/<slug>。
读取 WORKSTREAM.json、TODO.md、HANDOFF.md、EVIDENCE_AND_GATES.md、最新 JOURNAL 条目和 git status。
只分配 ready 的任务，并明确 owner、文件范围、依赖关系和验证命令。
如果已经存在完成的输出，先切到 $integrate-lane-results，再接受、提交、合并或选择全局下一步。
```

已知 Architecture lane planner prompt：

```text
使用 $plan-engineering-program 规划 architecture lanes。
读取 docs/architecture/LANES.md、active WORKSTREAM.json、git status、branches 和 worktrees。
批准哪个 lane 继续、哪个 lane 需要同步 main、哪个 lane 被 shared scopes 阻塞。
已完成 lane 输出要切到 $integrate-lane-results，经过 review 和新鲜验证后，再逐个集成。
```

## Result Inspection Prompt

当 worker 或 lane 终端完成后，integrator 用这个判断下一步。

```text
使用 $integrate-lane-results 检查 worktree <path> 的结果。
读取 git status、git diff、changed file scope、相关 TODO.md、EVIDENCE_AND_GATES.md、HANDOFF.md
本地 planner state 和 session tail，再考虑是否需要终端报告。
运行
skills/engineering/integrate-lane-results/scripts/inspect_worktree_result.py <path> --json
把 git state、workstream docs 和该 worktree 最新可见 assistant message 合并成 result-intake
证据，再考虑是否需要用户粘贴聊天。
把结果分类为 ACCEPT_FOR_REVIEW、NEEDS_FIX、NEEDS_VERIFY、BLOCKED、READY_TO_INTEGRATE 或 READY_FOR_NEXT_BUNDLE。
然后返回当前 integration 动作、review/verify 负责人、要设置的 Codex goal，以及给 lane/worker 终端的结构化 handoff block。
只有本地证据无法重建结果时，才要求用户粘贴聊天。
使用 Integration Action mode RESULT_INTAKE、REVIEW_VERIFY、INTEGRATION_SYNC 或 BLOCKED_DECISION。
不要让 worker 决定全局下一个任务。
```

## 状态 / 下一步 Prompt

当用户问当前这些终端接下来应该做什么时，用这个。

```text
使用 $plan-engineering-program 的 status/next-action 模式。
检查 active worktrees、branches、dirty status、active WORKSTREAM.json、TODO/evidence/handoff
状态、planner state 和终端报告。把每条 lane 分类为 RUNNING、ACCEPT_FOR_REVIEW、NEEDS_VERIFY、
READY_TO_INTEGRATE、READY_FOR_NEXT_BUNDLE、NEEDS_FIX 或 BLOCKED。
对 active 或 stale worktrees，可以把 result-intake helper 作为轻量补充上下文。
先说明当前上层架构终端现在要做什么，再给其他终端结构化 handoff block、精确 prompt 和有边界的 Codex goals。
不要在上层 planner 终端实现 worker task。
使用 Program Action mode RECON、ASSIGNMENT 或 DECISION。如果下一步是接受完成输出，切到 $integrate-lane-results。
```

## Lane Goal Bundles

Lane goal bundle 是批准给长期终端执行的工作单元。它应该大于一次机械小改，
小于整个 architecture lane。

包含：

- lane slug 和 worktree；
- 一个 active workstream 或短的同 lane 队列；
- 一到三个 ready task IDs；
- owned scopes 和 shared scopes；
- context manifest，例如 `docs/workstreams/<slug>/CONTEXT.jsonl`；
- validation commands；
- stop conditions。

Codex goal 只用于当前 bundle、campaign 或一个有边界任务，不用于整个 lane。
当任务、bundle 或 campaign 已经适合较长时间自动执行时，上层 planner 应该给出精确 goal 文本，
并明确询问是否由当前终端设置。如果当前对话里用户已经批准设置 goal，就直接设置这个有边界 goal。

## Lane Campaigns

当需求和文档足够清楚时，上层 planner 可以准备 autonomous lane campaign：把多个有序的同 lane
bundles 或 workstreams 放到一个更长的 Codex goal 下执行。

包含：

- campaign ID 和 lane worktree；
- 有序 bundle/workstream queue；
- 每一步 gates 和 evidence updates；
- auto-advance rule；
- 每一步后的 checkpoint；
- side-effect policy（`manual`、`auto-commit-sync` 或 `auto-commit-sync-merge`）；
- stop conditions 和明确的禁止规则。

Campaign 可以减少用户切换，但仍然有边界。它不能包含未 review 的 ADR 变更、不清楚的 shared
scopes、protected-branch push 操作或 cross-lane edits，除非上层 planner 明确列出且用户批准这些 side effects。

每个 campaign 都应该包含明确 side-effect policy。稳定 lane 工作优先用 `auto-commit-sync`：
在已接受 task/bundle 边界自动 commit，并在 clean gates 后把 main 同步回 lane worktree。
只有 integration order、post-merge gate 和 branch policy 都清楚时，才用 `auto-commit-sync-merge`。
如果用户没有预先批准 commit、sync、merge、worktree 创建或 related-repo changes，就用 `manual`。
遇到冲突、失败 gates、无关 dirty files、public contract 或 ADR/schema 变化、related-repo 决策、
protected branch 问题或未批准 push 时停止。

如果任务相关但不适合并行，上层 planner 应该明确说明，并用一个稳定 worktree 上的 **serial lane
campaign**。不要为了形式上多终端而开启会立刻 BLOCKED 的终端。lane 终端只有在每个任务 gate
通过且 evidence 已更新后，才按顺序自动推进。

Campaign goal prompt：

```text
把当前 Codex goal 设置为执行已批准的 lane campaign <CAMPAIGN-ID>。
只有每个 bundle 的 gate 通过且 evidence 已更新时，才自动推进下一步。
遇到 shared scopes、ADR/schema/contract 变更、失败 gate、缺失 context、无关 dirty files 或未批准 side effects 时停止。
```

Serial campaign goal prompt：

```text
把当前 Codex goal 设置为执行已批准的 serial lane campaign <CAMPAIGN-ID>。
使用这一个 lane worktree，按顺序执行任务；每个任务完成后更新 evidence，只有 gate 通过且没有触发 stop
condition 时才自动推进。遇到 ADR/schema/contract 变更、失败 gate、无关 dirty files、未批准 commit
或 planner-blocked shared scope 时停止。
```

## 长期 Lane 深化

如果某条 lane 要持续成熟，长期愿景应该存在 architecture docs 或 lane roadmap，而不是 Codex
goal。记录 current state、target maturity、capability gaps、active/draft/deferred workstreams、
validation ladder、shared scopes、related repos 和 next bundles。

当 lane 队列为空，或所有 bundle 都太小，先回到 `$plan-architecture-lane`，不要直接硬派新任务。
它应该做 source coverage audit；如果 lane seam 或 docs/code 对齐不清楚，再用 code-aware planning
或 scoped `$improve-codebase-architecture`。

不要等用户追问“有没有新任务”。如果边界已经稳定但 ready queue 变薄，上层 planner 应该主动检查
code/docs，挖掘同 lane 的深化候选。每个候选都要分类为 implement-now、plan-first、ADR-first、
wait-for-active-branch 或 defer；优先选择 crate 内部、验证清楚、避开活跃 hot files 的任务。

上层 planner 给 worker 或 lane 终端分配任务后，也可以在它们运行期间继续做只读 architecture
reconnaissance。它可以对全仓库或某个 lane 跑 scoped `$improve-codebase-architecture`、检查
docs/code drift，并准备下一波 candidate backlog。但不能在未明确批准时重写 active ledger、
修改 ADR、追加实现任务，或让正在运行的 bundle 失效。

## Workstream 过多

先把 workstream 过多当作状态治理问题处理，不要急着改目录结构：

- 保持 `docs/workstreams/<slug>/` 扁平，用 metadata/index 做 lane 分组。
- 分配终端前先盘点 `WORKSTREAM.json`。
- 开新 workstream 前，先关闭或拆分过时的 `active` workstreams。
- 每个 lane 只保留短 active queue，其余推迟。
- 不要随意移动旧 workstream 路径，除非链接和 ADR 引用都能保持稳定。

## 创建终端

上层 planner 负责推荐终端、worktree 路径、分支名、创建命令和提示词。它可以在用户批准后帮忙创建
worktree，也可以把命令交给用户执行。只有用户批准且角色有明确范围和验证路径时，才创建终端。

优先保持一个 architecture lane 一个长期 worktree，不要每个 workstream 新建一个 worktree。
在同一个 lane worktree 里连续推进队列，可以减少分支杂音、合并成本和 Rust `target/` 空间增长。

- 上层 planner / 主控终端：发现 active work，负责顺序、冲突和终端分配。
- Architecture lane 终端：长期负责一个能力域下的 workstream 队列。
- Worker 终端：只负责 `TODO.md` 里的一个有边界任务。
- Reviewer / verifier 终端：产出量大时单独开；否则上层 planner 可以负责 review 和验证，或用 `$integrate-lane-results` 接受完成输出。
- Docs / next-version 终端：探索未来计划，但不能重写当前 active ledger。

当 worker 报告 `DONE` 时，默认下一步不是让 worker 自己 review 自己。Integrator 或上层 planner
要么在当前终端做 review/verify，要么分配独立 reviewer/verifier 终端。worker 等待 review 修复请求和下一个
已批准的 task 或 bundle。

## Subagent Sidecars

稳定终端和 worktree 负责长期 lane 执行。Explorer subagents 是上层 planner 可以用于架构审查、
code-aware lane planning 或独立只读问题的临时 sidecar。它们的发现是 planner 证据；它们不拥有
planner state，不接受工作结果，不决定全局顺序，也不能在未批准时执行 side effects。

## Integration And Side Effects

上层 planner 和 integrator 可以自由分析。commit、merge 或 sync 只有在当前 campaign policy 预先批准时才自动执行；否则创建/删除 worktree、branch 操作、shared-scope edits、commit、merge、push 或修改相关仓库前必须询问用户。结果检查后，一次只集成一个 lane branch：先 review，再用新鲜证据 verify，只提交批准的变更，按批准顺序 merge/sync，然后更新 planner state 和下一个要设置的 Codex goal。

在已接受的 task 或 bundle 边界提交。另一条 lane 依赖该切片、shared scopes 变化、bundle /
workstream slice 完成，或分支差异开始形成风险时，再合并回 main。完成已接受合并后、开启新
bundle 前或触碰 shared scopes 前，把 main 同步回活跃 lane worktrees。

## Cross-Repo Coordination

当工作跨相关仓库时，把每个 repo 纳入 bundle：path、branch、dirty state、owned scope、
validation 和 integration order。相关 repo 需要用户决策、ADR、version bump 或 release note
时停止。

## Architecture Lane Prompt

```text
使用 $run-architecture-lane 负责 <lane> lane。
把当前 Codex goal 设置为完成已批准的 lane bundle <BUNDLE-ID> 或 lane campaign <CAMPAIGN-ID>。
保持这个终端在该 lane 的 worktree 中，持续推进该能力域下的 workstream 队列；遇到 shared scopes、ADR 变更、schema 变更或 server 契约变更时停止并请求上层 planner 协调。
把已批准的 lane bundle 或 campaign 作为最大自主范围。
只推荐同 lane 下一步；全局顺序由上层 planner 负责。
```

## Worker Prompt

```text
使用 $run-workstream-task 执行 docs/workstreams/<slug>/TODO.md 里的任务 <TASK-ID>。
你是 Worker <id>。你不是这个代码库里唯一工作的 agent。
保持在分配的文件范围内。
编辑前读取分配的 context manifest 或 task-specific context。
不要重写全局计划。
不要回退用户或其他 worker 的变更。
最终状态必须是 DONE、DONE_WITH_CONCERNS、BLOCKED 或 NEEDS_CONTEXT。
汇报变更文件、验证结果、evidence updates、concerns、阻塞项、handoff notes，以及推荐的同 lane 下一步。
不要自行决定全局下一个任务。
可以提出 follow-up 或 task split，但不要改变 workstream target state。
最后提醒用户把这份报告交回上层 planner 或 integrator，由其安排 review、verification 和下一个批准的 task 或 bundle。
```

## Reviewer Prompt

```text
使用 $review-workstream 根据 workstream 的 DESIGN.md、TODO.md、EVIDENCE_AND_GATES.md、仓库
AGENTS.md 和相关 ADR review 已完成的 worker tasks。先报告 findings，再报告残余风险和缺失 gates。
```

## Verifier Prompt

```text
使用 $verify-rust-workstream 用新鲜命令证据验证已 review 的任务或 lane，然后上层 planner 或 integrator 才能标记完成。
```

## Docs / Next-Version Prompt

```text
使用 $grill-with-docs 或 $to-prd 准备下一版本方案。
不要重写当前 active workstream 的目标或 TODO.md。
产出 ADR candidates、PRD/spec notes、prototype findings，或 proposed follow-on workstream。
```

## 集成规则

Worker 更新自己的 task notes、evidence notes、journal/handoff entries。Integrator / 上层 planner 负责把结果集成到全局任务顺序、owner 分配、milestone 状态和 closeout 决策。

## 停止条件

出现以下情况时，停止并行执行，回到上层 planner / integrator 协调：

- 两个 worker 需要同一片文件区域。
- 任务改变 workstream target state。
- 任务暴露 ADR 级别决策。
- 验证无法独立运行。
- worker 输出和 workstream contract 冲突。

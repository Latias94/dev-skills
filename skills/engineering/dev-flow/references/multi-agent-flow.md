# Multi-Agent Flow

## Roles

**Upper Architecture Planner**
: Owns the engineering program, lane maps, lane roadmaps, campaign queues, dependency order, and
global conflict resolution.

**Architecture Lane Terminal**
: Owns one capability area across a sequence of workstreams, such as storage, transcode, playback,
or admin. It should use `run-architecture-lane` and may propose the next same-lane medium goal.

**Worker**
: Owns one bounded task from the ledger.

**Reviewer**
: Checks implementation against both repository standards and workstream intent.

**Integrator**
: Uses `integrate-lane-results` to inspect worktree results, route review/verify, and propose
commit/merge/sync actions.

## Launch Criteria

Use multiple agents only when:

- `plan-architecture-lane` has chosen planning depth and any needed code-aware or architecture
  review pass is complete,
- tasks or architecture lanes are independent enough to run in parallel,
- file scopes are disjoint or clearly serialized,
- validation can be run per task,
- and the upper planner or integrator can integrate results.

Keep the work local when the next step depends on one unresolved design decision.

## Parallel Work Pattern

1. Upper planner updates `TODO.md` with task IDs, owners, dependencies, scopes, validation, and required
   context.
2. Upper planner prepares `CONTEXT.jsonl` when the workstream will use lane terminals or parallel
   workers.
3. Upper planner creates a lane goal bundle, or a lane campaign when several ready bundles can run safely.
4. Upper planner writes the Codex goal to set or asks whether to set it for each approved task, bundle, or campaign.
5. Each worker receives one task ID and an explicit file/module scope.
6. Workers update only:
   - their task status,
   - relevant evidence notes,
   - a journal entry or handoff.
7. Integrator inspects results, routes review/verify, and resolves conflicts with the upper planner.
8. Reviewer uses `review-workstream` for contract and code-quality checks.
9. Integrator uses `verify-rust-workstream` before accepting completion.

## Subagents Vs Terminals

Terminals and worktrees are durable execution lanes. They can own a lane, branch, task bundle, and
runtime state.

Subagents are temporary sidecars. Use them when the invoked workflow calls for delegated
architecture review, code-aware planning, or multi-agent coordination, and when they can answer a
bounded question or perform a disjoint task without owning global state. Good uses are independent
code exploration during `plan-architecture-lane`, read-only review sidecars, or tightly scoped
worker patches with disjoint write sets.

Subagent findings become planning evidence. They do not choose global sequencing, accept worker
output, create worktrees, commit, merge, or update planner state by themselves.

## Subagent Opportunity Matrix

| Workflow | Good subagent use | Avoid |
| --- | --- | --- |
| `audit-project-scale` | Explorers summarize crates, docs, workstreams, and gates in a large repo | Writing setup files |
| `plan-architecture-lane` | Explorers inspect lane call flow, test seams, shared scopes, and docs/code drift | Choosing target state |
| `improve-codebase-architecture` | Explorers walk different areas for deepening candidates | Proposing implementation plans too early |
| `open-workstream` | Explorers confirm impacted files, validation commands, and existing ADRs | Editing the task ledger directly |
| `plan-engineering-program` | Explorers inspect lane seams, architecture drift, and deepening candidates | Mutating active ledgers without approval |
| `integrate-lane-results` | Sidecars inspect independent worktree results or diff risks | Accepting worker output |
| `review-workstream` | One sidecar checks contract compliance while another checks code quality | Fixing findings |
| `diagnose` | After a repro loop exists, sidecars test independent hypotheses | Guessing without the loop |
| `fearless-refactor` | Explorers map deletion candidates and coupling before splitting work | Broad shared-scope writes |

## Architecture Lane Pattern

Use architecture lanes when the same terminal should keep advancing a capability area over multiple
workstreams.

1. Assign one lane per terminal, such as `storage`, `transcode`, or `playback`.
2. Give the terminal a lane goal bundle: one to three ready tasks, context manifest, validation, and
   stop conditions.
3. Record owned scopes and shared scopes. Shared scopes require upper-planner coordination.
4. Keep the terminal/worktree stable, but prefer one short-lived branch per workstream.
5. Close and verify the current workstream before starting the next queued workstream.
6. Refresh the lane roadmap/backlog when the queue is empty or all remaining tasks are too small.
7. Stop the lane terminal when the bundle is done, blocked, missing context, or touches shared
   scope.

When the queue is thin, either the lane terminal proposes a same-lane next medium goal or the upper
planner proactively mines candidates. Use `plan-engineering-program`, `plan-architecture-lane`,
scoped `improve-codebase-architecture`, or explorer sidecars to inspect code/docs and classify
candidates as implement-now, plan-first, ADR-first, wait-for-active-branch, or defer.

After lane terminals are dispatched, the upper planner may use idle time for read-only architecture
reconnaissance: scoped repo or lane review, docs/code drift checks, and next-wave backlog discovery.
It should not rewrite active ledgers, change ADRs, or assign extra implementation while workers are
running without explicit approval.

## Lane Goal Bundle Sizing

Use a bundle when Codex should run for longer than one small task without constant user switching.
The bundle should be:

- bigger than a single mechanical edit,
- smaller than a whole architecture area,
- limited to one lane and one stable worktree,
- backed by `TODO.md` task IDs and a context manifest,
- validated by commands the lane terminal can run,
- stopped by clear blockers or shared-scope changes.

When the bundle is ready for longer autonomous work, recommend or ask to set a Codex goal for the
bundle or one bounded task, not for the whole lane.

If the user wants sustained lane deepening, keep the long-term target in architecture docs and make
the next Codex goal only the current ready bundle or approved campaign.

If enough implement-now candidates share one lane, the planner can turn them into a campaign so the
lane terminal runs longer with fewer user interventions.

When tasks are not parallelizable but form a clear dependency chain, prefer one serial lane campaign
on a stable worktree over repeated one-task prompts. The upper planner should explain that the work is not
parallel, write a longer goal, and allow auto-advance only after each step's gates and evidence pass.

## Worker Prompt Shape

```text
You are Worker <id>. You are not alone in the codebase.
Own task <TASK-ID> from docs/workstreams/<slug>/TODO.md.
Do not rewrite global scope, target state, or unrelated tasks.
Do not revert user or other worker changes.
Touched file scope: <paths>.
Required context: <CONTEXT.jsonl entries or task-specific docs>.
Validation: <commands>.
Final status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT.
Final response: changed files, validation, evidence updates, concerns, and proposed follow-ups.
```

## Worker Status Protocol

- `DONE`: implementation and task-local validation completed.
- `DONE_WITH_CONCERNS`: completed, but reviewer/integrator should inspect named concerns before accepting.
- `BLOCKED`: cannot finish without task split, design change, or external input.
- `NEEDS_CONTEXT`: needs missing repo, workstream, or requirement context before continuing.

## Stop Conditions

Stop and escalate to the upper planner or integrator when:

- the task requires changing an ADR or workstream target state,
- another worker owns the same file region,
- validation is impossible with the current task split,
- or the implementation reveals the task is the wrong vertical slice.

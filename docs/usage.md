# Usage

Chinese documentation: [zh-CN/usage.md](./zh-CN/usage.md)

Most users should start with `$dev-flow`.

`$dev-flow` is the orchestrator. It should actively delegate to the next skill instead of only
telling the user what to do next.

Use `$audit-project-scale` first when the repo is unfamiliar, old workflow docs may be stale, or you
are deciding whether multiple terminals and architecture lanes are justified.

Use `$shape-product-architecture` when the input is still a product ambition rather than a concrete
engineering lane: it turns vision, reference products, MVP stages, capability boundaries, and ADR
candidates into planning artifacts before workstreams are opened.

For large projects, use `$run-architecture-lane` when one terminal should keep owning a capability
area such as storage, transcode, playback, realtime, or admin.

Use `$plan-engineering-program` for the upper architecture terminal that owns lane maps, campaign
queues, and macro sequencing. Use `$integrate-lane-results` when a lane or worktree reports output
that needs review, verification, merge, or sync.

## Choose By Repo Size

| Situation | Skill to call | Notes |
| --- | --- | --- |
| Broad product goal or unclear MVP | `$shape-product-architecture` | Shape vision, MVP ladder, capability map, lanes, and ADR candidates first. |
| Small repo, one bounded change | `$dev-flow` | Let it route to `tdd` or `diagnose`; avoid heavy docs. |
| Medium repo, multi-step change | `$dev-flow` | Open or reuse one workstream when traceability matters. |
| Large repo, capability-scoped worktrees | `$audit-project-scale` first | Prefer one stable worktree per lane; planner asks before creating. |
| Multiple active terminals | `$plan-engineering-program` | Use an upper architecture terminal or your main control terminal. |
| Too many workstreams | `$plan-engineering-program` | Run inventory, close stale active lanes, and keep only a short active queue. |
| Old workstream or architecture docs | `$audit-project-scale` | Repair substrate before adding new workstreams. |

## Common User Calls

Initialize a project:

```text
Use $dev-flow to initialize this Rust repo for the dev-skills workflow.
```

Audit workflow scale:

```text
Use $audit-project-scale on this Rust repo. Decide whether it should stay lightweight, use normal
workstreams, or add architecture lanes and upper-planner coordination.
```

Plan a large feature:

```text
Use $dev-flow to plan this feature. Clarify requirements if needed, then create or reuse the right
workstream and split executable tasks.
```

Shape a product architecture:

```text
Use $shape-product-architecture to turn this product goal into a bounded vision, MVP ladder,
capability map, architecture lanes, ADR candidates, and initial workstream priorities.
```

Plan a selected architecture direction:

```text
Use $dev-flow to plan the storage lane. Choose planning depth, inspect docs/code alignment, and
route to $plan-architecture-lane before creating workstreams or lane bundles.
```

Implement a bounded task:

```text
Use $dev-flow to execute task ABC-020 from docs/workstreams/<slug>/TODO.md.
```

Debug a failure:

```text
Use $dev-flow to diagnose this failing test and record regression evidence in the active workstream.
```

Prepare a handoff:

```text
Use $dev-flow to prepare a handoff for the current workstream.
```

Discover a multi-terminal plan:

```text
Use $plan-engineering-program to inspect this repo, identify active workstreams or architecture lanes,
and recommend planner, lane, worker, reviewer, and docs terminals. Prefer one stable worktree per
architecture lane and ask before creating worktrees or branches.
```

Plan a known workstream in the upper architecture terminal:

```text
Use $plan-engineering-program to plan docs/workstreams/<slug> across upper-planner, worker, reviewer,
and docs terminals.
```

Plan architecture lanes:

```text
Use $plan-engineering-program to plan architecture lanes, shared scopes, lane campaigns, branch sync points, and integration order.
```

Inventory many workstreams:

```text
Use $plan-engineering-program to inventory docs/workstreams, summarize active/draft workstreams by lane,
identify stale or missing lane metadata, and recommend which workstreams to close, keep active, or defer.
```

Inspect a completed worktree result:

```text
Use $integrate-lane-results to inspect the result in worktree F:\SourceCodes\Rust\nako-worktrees\<lane-worktree>.
Read git status, git diff, related workstream TODO/evidence/handoff, local planner state, and session tails before asking for a report.
Use the integrate-lane-results helper for that worktree before asking me to paste chat:
skills/engineering/integrate-lane-results/scripts/inspect_worktree_result.py <worktree> --json
Decide whether the result is ACCEPT_FOR_REVIEW, NEEDS_FIX, NEEDS_VERIFY, BLOCKED, or READY_FOR_NEXT_BUNDLE.
Then give the next integration action, Codex goal to set, and structured handoff block for the lane or worker terminal.
Ask me for pasted chat only when local evidence cannot reconstruct the result. Do not let the worker choose the global next task.
```

Run a long-lived architecture terminal:

```text
Use $run-architecture-lane for the storage lane. Keep this terminal on storage/VFS workstreams and stop when shared database or server contracts need coordination.
```

Review and verify a completed task:

```text
Use $dev-flow to review and verify task ABC-020 before marking it complete.
```

Recover a broken Codex session:

```text
Use $codex-session-recovery to recover continuation context from the latest Codex session.
```

## Direct Specialist Skill Calls

Call these directly when you want that explicit action, rather than the normal development router.

Configure issue tracker/domain docs:

```text
Use $setup-matt-pocock-skills to configure AGENTS.md and docs/agents for this repo.
```

Pressure-test an idea before project docs exist:

```text
Use $grill-me to challenge this project idea until the MVP, non-goals, and risks are precise.
```

Pressure-test a plan against existing docs:

```text
Use $grill-with-docs to pressure-test this plan against CONTEXT.md, ADRs, and active workstreams.
```

Understand unfamiliar code:

```text
Use $zoom-out to explain how this subsystem fits into the larger project.
```

Review architecture:

```text
Use $improve-codebase-architecture to find crate-boundary, module-depth, and testability problems.
```

Execute architecture refactoring:

```text
Use $fearless-refactor on the top recommendation from the architecture report and route it through $dev-flow.
```

Prepare release notes:

```text
Use $changelog to update CHANGELOG.md from the latest tag to HEAD.
```

Commit reviewed work:

```text
Use $commit-work to commit only the reviewed workstream changes. Inspect all dirty files, stage only approved paths, use Conventional Commits, run the relevant check, and report remaining dirty files.
```

Build a throwaway experiment:

```text
Use $prototype to test two designs before we commit to an ADR.
```

Export to project tracker:

```text
Use $to-prd to turn this clarified plan into a PRD, then $to-issues if it should become GitHub issues.
```

Create a reusable skill:

```text
Use $write-a-skill to create a project-specific skill for this repeated workflow.
```

## Manual Recovery Skill

Call `$codex-session-recovery` directly after a Codex crash, context corruption,
`invalid_encrypted_content`, or when a new chat needs to reconstruct what happened in a previous
session. It reads Codex session JSONL files and returns recovery evidence; project docs and git state
still outrank recovered transcript content.

```text
Use $codex-session-recovery to read this Codex session id and reconstruct the active goal, recent tool activity, compaction summary, and safe continuation plan: 019e2779-da60
```

## Default User Experience

```text
User -> $dev-flow -> delegated skill -> $dev-flow resumes routing
```

The user should not need to remember internal workflow skills. `$dev-flow` should decide whether the
next move is bootstrap, grill, workstream planning, TDD execution, diagnosis, review, or handoff.
Use `$audit-project-scale` when the workflow scale itself is the question. `$run-architecture-lane`
is the default entrypoint for large-project lane terminals. `$shape-product-architecture` is the
default entrypoint when the question is product/MVP/capability shaping rather than implementation.

When the next step is not obvious, the agent should state the current phase, recommended route,
evidence read, side effects needing approval, expected artifact or terminal prompt, and next likely
phase. Prefer a concrete recommendation over asking the user to choose from internal skills.

Example chain:

```text
User asks for large feature
-> $dev-flow detects unclear requirements
-> delegates to $grill-with-docs
-> resumes and delegates to $open-workstream
-> creates task ledger
-> delegates multi-terminal planning to $plan-engineering-program when needed
-> delegates first task to $tdd or $diagnose
-> reviews completed work with $review-workstream
-> verifies fresh evidence with $verify-rust-workstream
-> records evidence and handoff
```

## Codex Goals

Codex goals are useful for one bounded task from a workstream task ledger, or for one approved lane
goal bundle or lane campaign.

When the task, lane bundle, or lane campaign is clear enough for longer autonomous work, the planner should
recommend the exact goal text and explicitly ask whether this terminal should set it. If the user
has already approved goal setup in the current conversation, set the bounded goal directly. Do not
wait for the user to know that a goal is useful.

Use goals for:

- one task ID from `TODO.md`,
- one approved lane goal bundle,
- one approved lane campaign with ordered bundles and auto-advance gates,
- a single bug fix,
- a bounded validation loop.

Do not use goals for:

- the whole workstream,
- the whole architecture lane,
- long-term architecture memory,
- replacing ADRs or workstream docs.

For long-term lane deepening, ask the upper planner to maintain a lane roadmap or architecture doc with
current state, target maturity, capability gaps, active/draft/deferred workstreams, validation
ladder, shared scopes, and next bundles. The Codex goal should still be one current bundle.
When several ready bundles are ordered and well-gated, the upper planner may instead propose a lane
campaign so one goal can run longer with checkpoints and stop conditions.

Recommended pattern:

```text
1. $open-workstream creates task ABC-020.
2. User asks Codex to set ABC-020 as the current goal.
3. Agent executes and validates the task.
4. Agent reviews the output and runs fresh verification.
5. Agent marks the goal complete only after the task is genuinely done.
6. Agent updates TODO.md and EVIDENCE_AND_GATES.md.
```

Lane bundle pattern:

```text
1. Upper planner approves bundle storage-20260530-01 with task IDs, scope, context, validation, and stop conditions.
2. User asks the lane terminal to set that bundle as the current Codex goal.
3. Lane terminal runs until the bundle is done or a stop condition appears.
4. Lane terminal writes a structured handoff block with DONE, DONE_WITH_CONCERNS, BLOCKED, or NEEDS_CONTEXT.
5. Integrator reviews, verifies, and chooses the next global action with the upper planner when needed.
```

Lane campaign pattern:

```text
1. Upper planner prepares campaign storage-20260531-01 with an ordered queue of bundles, gates, checkpoints, and stop conditions.
2. User asks the lane terminal to set that campaign as the current Codex goal.
3. Lane terminal auto-advances through the listed bundles only when each gate passes.
4. Lane terminal stops on failed gates, shared scopes, ADR/schema/contract changes, missing context, or unapproved side effects, then writes a structured handoff block.
5. Integrator reviews, verifies, integrates, and asks the upper planner to refresh the next campaign if needed.
```

Use a serial lane campaign when tasks are dependency-ordered and not parallelizable. It should keep
one terminal busy on one worktree, auto-advancing only after per-step gates and evidence pass.

## Internal Workflow Skills

These are normally invoked by `$dev-flow`, not manually:

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

Directly call one only when you intentionally want to bypass the router, when the upper architecture
terminal is planning multiple lanes with `plan-engineering-program`, or when completed lane output
needs `integrate-lane-results`.

## Multi-Agent Use

Only parallelize when tasks have clear boundaries.

Upper architecture prompt:

```text
Use $plan-engineering-program to inspect this repo and prepare a multi-terminal plan.
Start with Program Action Mode, Now, and Why.
Do not assume a current workstream. Recommend terminals only when scopes, branches, dependencies,
and validation commands are clear. Prefer one stable worktree per architecture lane. Ask before
creating worktrees or branches, and include lane goal bundles, proposed commands, context
manifests, optional lane campaigns, Codex goals to set after approval, and terminal prompts.
List three to five large candidate directions when the repo supports them, but activate at most
three lane/worker terminals by default. Use one planner/recon terminal or one serial campaign when
architecture substrate, lane maps, or module boundaries are still unclear.
Include WIP count, assignment go/no-go, expected autonomy horizon, and integration bottleneck risk.
For long-running campaigns, choose an upfront side-effect policy: `manual`, `auto-commit-sync`, or
`auto-commit-sync-merge`; include deny rules for conflicts, failed gates, unrelated dirty files,
ADR/schema/public contract changes, related-repo decisions, protected branch issues, and
unapproved pushes.
Upper planner owns workstream creation/reuse, task ledgers, lane bundles, and global sequencing; lane and
worker terminals implement assigned work and report back.
Use $plan-architecture-lane to choose planning depth before creating workstreams or bundles; it may
route to $improve-codebase-architecture when lane seams or docs/code alignment are unclear.
When the lane queue is too thin, refresh the lane backlog before assigning more work. Do not only
consume existing TODOs; inspect code/docs and proactively propose same-lane deepening candidates
that are implement-now, plan-first, ADR-first, wait-for-active-branch, or defer.
After assigning workers or lane terminals, use idle planner time for read-only architecture
reconnaissance when no integration/review work is pending. Scoped $improve-codebase-architecture
passes may inspect the whole repo or individual lanes, but findings become proposed candidates, not
unapproved active-ledger or ADR edits.
Spend agent time before spending user attention. Use $zoom-out for unfamiliar code,
$improve-codebase-architecture for thin lane queues or docs/code drift, and $grill-with-docs only
when a product or domain decision is genuinely unclear.
Choose the program mode that fits the state: DISCOVERY, SHAPE, PLAN, ASSIGN, RECON, or DECISION.
If candidate tasks are not parallelizable but can run as an ordered dependency chain, propose one
serial lane campaign on a stable worktree instead of repeatedly asking for one-task prompts.
Write the exact Codex goal to set for each approved task, lane bundle, or lane campaign, never for an entire lane.
For clear deep work, propose a lane campaign instead of a tiny bundle chain.
Ask only for worktree, branch, commit, merge, push, shared-scope, related-repo side effects not
covered by the campaign policy, or real product/architecture decisions after presenting the best
recommendation.
```

For large multi-worktree work, the planner may keep local runtime state in
`.codex/planner-state.local.json`; do not commit personal absolute paths. The state may include
terminal IDs, session refs for recovery, lane goal bundles, and context manifests. Session refs are
pointers, not authority.

Worker prompt:

```text
Use $run-workstream-task to execute task ABC-020. It should delegate to $tdd or $diagnose as needed,
read assigned context before editing, stay within the assigned file scope, update the task ledger
and journal, and recommend a same-lane next action when done. Do not choose the global next task.
Propose follow-ups or splits in the final report instead of changing the workstream target state.
End by telling the user to return the report to the planner for review, verification, and the next
approved task or bundle.
```

Reviewer prompt:

```text
Use $review-workstream to review completed task ABC-020 against the workstream contract and repo
standards.
```

Verifier prompt:

```text
Use $verify-rust-workstream to verify task ABC-020 with fresh command evidence before completion.
```

Workers should not rewrite the global task ledger or redefine the workstream target state.

## Skill Delegation

When a skill hands off to another skill, it should pass the minimum durable context:

- workstream path,
- task ID,
- file scope,
- context manifest or task-specific context,
- validation command,
- relevant ADR/docs,
- and expected output artifact.

Example:

```text
Delegate to $tdd:
Task: ABC-020
Workstream: docs/workstreams/<slug>
Scope: crates/foo/src/**
Validation: cargo nextest run -p foo abc_020
Expected output: code changes, passing validation, TODO.md status update, evidence note
```

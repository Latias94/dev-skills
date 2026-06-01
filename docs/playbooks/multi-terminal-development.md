# Multi-Terminal Development

Chinese documentation: [../zh-CN/playbooks/multi-terminal-development.md](../zh-CN/playbooks/multi-terminal-development.md)

Use this playbook when one workstream needs multiple Codex terminals, or when a large project uses
one terminal per architecture lane.

If you are not sure the repo needs this much coordination, run `$audit-project-scale` first and
stay on `$dev-flow` for small or medium work.

## Terminal Map

```text
Terminal 1: Upper architecture planner / commander
Terminal 2: Architecture lane A
Terminal 3: Architecture lane B
Terminal 4: Worker or diagnosis sidecar
Terminal 5: Reviewer / verifier / integrator
Terminal 6: Docs / next-wave planning
```

The upper architecture planner can be a separate terminal or your main control terminal. It owns
workstream creation/reuse, lane roadmaps, global sequencing, shared-scope decisions, and task-ledger
changes. Lane and worker terminals implement approved campaigns, bundles, or tasks and report back.
The canonical role contract lives in
`skills/engineering/dev-flow/references/multi-agent-flow.md`; keep this playbook as usage guidance.
Structured terminal result markers live in
`skills/engineering/dev-flow/references/agent-contracts.md`.

For architecture-lane work, the upper planner owns cross-lane priorities and shared scopes. Lane
terminals own capability areas such as storage, transcode, playback, realtime, or admin.

Upper-planner replies should use the current-terminal perspective. Start with what this terminal
should do now, then list prompts to paste into other terminals. If this terminal will run result
inspection, review, or fresh verification, say so directly instead of saying "ask planner/reviewer".

## Upper Planner State

For multi-worktree work, keep runtime facts in local `.codex/planner-state.local.json` or
`docs/local/PLANNER_STATE.md`. Track repo path, branch, head, dirty status, lane/workstream, active
task, lane goal bundle, context manifest, session refs, shared scopes, validation, and related
repositories. Commit examples and lane names only, not personal absolute paths. Workstream
`TASKS.jsonl` and `CAMPAIGNS.jsonl` hold durable task/campaign state; planner state records where
that state is running locally.

Use `session_refs` as recovery pointers only. Upper-planner decisions should come from workstream
docs, terminal reports, git state, and fresh verification, not raw chat history.

## Report Shapes

Upper-planner output should be state-shaped, not one fixed template. Program planning reports start
with:

```text
Mode: DISCOVERY | SHAPE | PLAN | ASSIGN | RECON | DECISION
Now: what this upper architecture terminal should do next
Why: one sentence grounded in repo evidence
```

Integration reports start with:

```text
Mode: RESULT_INTAKE | REVIEW_VERIFY | INTEGRATION_SYNC | BLOCKED_DECISION
Now: what this integration terminal should do next
Why: one sentence grounded in repo evidence
```

Use tables for lane/worktree status, numbered `Files / Problem / Solution / Benefits` candidates
for architecture reconnaissance, and fenced prompts for terminal copy/paste. Do not default to HTML;
use HTML only for a durable dashboard or artifact the user explicitly asks for.
Every upper-planner report should include `Minimal User Input Needed`; leave it empty or say
`None` when repo evidence is enough.

## User Attention Rule

Do not ask the user to find the next task while repo evidence can be inspected. Spend read-only
agent time on architecture docs, workstreams, git state, code paths, `zoom-out`, and scoped
`improve-codebase-architecture` before asking. Ask only for side effects not covered by the
campaign policy, product direction, ADR/schema/public-contract decisions, related-repo actions, or a
real tradeoff after giving the best recommendation.

## Program Discovery Prompt

Use this when you do not already know which workstream or lane should be active.

```text
Use $plan-engineering-program to inspect this repo and recommend a multi-terminal plan.
Do not assume there is a current workstream.
Read docs/architecture/LANES.md, WORKSTREAM_LINKS.md, docs/workstreams/*/WORKSTREAM.json,
TASKS.jsonl, CAMPAIGNS.jsonl, git status, git worktree list, and documented related repositories.
Run `skills/engineering/plan-engineering-program/scripts/program_status.py <repo>` and
`skills/engineering/plan-engineering-program/scripts/validate_orchestration_state.py <repo>` when
the project has machine-readable orchestration artifacts.
Use `skills/engineering/dev-flow/references/artifact-contracts.md`,
`skills/engineering/dev-flow/references/gate-taxonomy.md`,
`skills/engineering/dev-flow/references/worktree-safety.md`, and
`skills/engineering/dev-flow/references/context-budget.md` when assignment readiness is unclear.
Create or reuse workstreams only when the durable scope and gates are clear.
Use $plan-architecture-lane for selected architecture directions; it chooses planning depth and may
route to scoped $improve-codebase-architecture when lane seams or docs/code alignment are unclear.
Use $zoom-out for unfamiliar code before planning, and scoped $improve-codebase-architecture when
the ready queue is thin or long-term lane depth is unclear.
Report candidate active workstreams or lanes, proposed lane goal bundles, Codex goals to set after
approval, recommended terminals, existing or new worktree paths, branch sync blockers, proposed
creation commands, terminal prompts, context manifests, and the first task each terminal should run.
Use Program Action mode DISCOVERY, SHAPE, PLAN, or ASSIGN.
Do not create new worktrees or branches until the user approves the plan.
```

## Known Workstream Planning Prompt

Use this when the workstream path is already known.

```text
Use $plan-engineering-program to plan docs/workstreams/<slug>.
Read WORKSTREAM.json, TODO.md, TASKS.jsonl, CAMPAIGNS.jsonl, HANDOFF.md, EVIDENCE_AND_GATES.md,
latest JOURNAL entries, and git status. Assign only ready tasks with owners, file scopes,
dependencies, and validation commands.
If completed output already exists, switch to $integrate-lane-results before accepting, committing,
merging, or choosing the next global action.
```

Known architecture-lane planner prompt:

```text
Use $plan-engineering-program to plan architecture lanes.
Read docs/architecture/LANES.md, active WORKSTREAM.json files, git status, branches, and worktrees.
Approve which lane continues, which lane must sync main, and which lane is blocked by shared scopes.
For completed lane output, switch to $integrate-lane-results and integrate one branch at a time
after review and fresh verification.
```

## Result Inspection Prompt

Use this when a worker or lane terminal finished and the integrator needs to decide what happens
next.

```text
Use $integrate-lane-results to inspect the result in worktree <path>.
Read git status, git diff, changed file scope, related TODO.md, EVIDENCE_AND_GATES.md, HANDOFF.md,
local planner state, and session tails before asking the user for a report.
Run
skills/engineering/integrate-lane-results/scripts/inspect_worktree_result.py <path> --json
to combine git state, workstream docs, and the latest visible assistant message before asking the
user to paste chat.
Classify the result as ACCEPT_FOR_REVIEW, NEEDS_FIX, NEEDS_VERIFY, BLOCKED, READY_TO_INTEGRATE, or
READY_FOR_NEXT_BUNDLE.
Then return the current integration action, review/verify owner, Codex goal to set, and structured
handoff blocks for the lane or worker terminals. Ask the user for chat text only when local evidence
cannot reconstruct the result.
Use Integration Action mode RESULT_INTAKE, REVIEW_VERIFY, INTEGRATION_SYNC, or BLOCKED_DECISION.
Do not let the worker choose the global next task.
```

## Status / Next Action Prompt

Use this when the user asks what the active terminals should do now.

```text
Use $plan-engineering-program in status/next-action mode.
Inspect active worktrees, branches, dirty status, active WORKSTREAM.json files, TODO/evidence/handoff
state, planner state, and terminal reports. Classify each lane as RUNNING, ACCEPT_FOR_REVIEW,
NEEDS_VERIFY, READY_TO_INTEGRATE, READY_FOR_NEXT_BUNDLE, NEEDS_FIX, or BLOCKED.
Use the result-intake helper as lightweight supplementary context for active or stale worktrees.
Lead with what this upper architecture terminal should do now, then provide structured handoff
blocks, exact prompts, and bounded Codex goals for other terminals. Do not implement worker tasks in
the upper planner terminal.
Use Program Action mode RECON, ASSIGN, or DECISION. If the next action is accepting completed
output, switch to $integrate-lane-results.
```

## Lane Goal Bundles

A lane goal bundle is the approved unit for long-running terminals. It should be bigger than
one mechanical edit and smaller than a whole architecture area.

Include:

- lane slug and worktree,
- one active workstream or a short same-lane queue,
- one to three ready task IDs,
- owned and shared scopes,
- context manifest such as `docs/workstreams/<slug>/CONTEXT.jsonl`,
- validation commands,
- stop conditions.

Use Codex goals only for a current bundle, campaign, or one bounded task, not for an entire lane.
When a task, bundle, or campaign is ready for longer autonomous work, the upper planner should
recommend the exact goal text and explicitly ask the user whether this terminal should set it. If
the user has already approved goal setup in the current conversation, set the bounded goal directly.

## Lane Campaigns

When requirements and docs are clear enough, the upper planner may prepare an autonomous lane
campaign:
several ordered same-lane bundles or workstreams under one longer Codex goal.

Include:

- campaign ID and lane worktree,
- ordered bundle/workstream queue,
- per-step gates and evidence updates,
- auto-advance rule,
- checkpoints after each step,
- side-effect policy (`manual`, `auto-commit`, `auto-commit-sync`, or `auto-commit-sync-merge`),
- stop conditions and explicit deny rules.

Campaigns reduce user switching, but they are still bounded. They cannot include unreviewed ADR
changes, unclear shared scopes, protected-branch push operations, or cross-lane edits unless the
upper planner explicitly lists and the user approves those side effects.

Every campaign includes an explicit side-effect policy. Use `auto-commit` when only local commits
are pre-approved. Prefer `auto-commit-sync` for stable lane work: auto-commit at accepted
task/bundle boundaries, then sync main into the lane worktree after clean gates. Use
`auto-commit-sync-merge` only when the integration order, post-merge gate, and branch policy are
clear. Use `manual` when the user has not pre-approved commits, sync, merge, worktree creation, or
related-repo changes. Stop before conflicts, failed gates, unrelated dirty files, public contract or
ADR/schema changes, related-repo decisions, protected branch issues, or unapproved pushes.

If tasks are related but not safe to parallelize, the upper planner should say so and use a single
**serial lane campaign** on one stable worktree. Do not open extra terminals just to block them. The
lane terminal may auto-advance through ordered tasks only after each task's gates pass and evidence
is updated.

Campaign goal prompt:

```text
Set the current Codex goal to execute approved lane campaign <CAMPAIGN-ID>.
Auto-advance through the listed bundles only when each gate passes and evidence is updated.
Stop on shared scopes, ADR/schema/contract changes, failed gates, missing context, dirty unrelated
files, or unapproved side effects.
```

Serial campaign goal prompt:

```text
Set the current Codex goal to execute approved serial lane campaign <CAMPAIGN-ID>.
Use this one lane worktree. Run the ordered tasks in sequence; after each task, update evidence and
auto-advance only if gates pass and no stop condition fires. Stop before ADR/schema/contract changes,
failed gates, dirty unrelated files, unapproved commits, or planner-blocked shared scopes.
```

## Long-Running Lane Deepening

For a lane that should keep maturing beyond the current queue, store the durable ambition in
architecture docs or a lane roadmap, not in the Codex goal. Track current state, target maturity,
capability gaps, active/draft/deferred workstreams, validation ladder, shared scopes, related repos,
and next bundles.

When the lane queue is empty or all bundles are too small, return to `$plan-architecture-lane` before
assigning more work. It should run a source coverage audit and use code-aware planning or scoped
`$improve-codebase-architecture` when lane seams or docs/code alignment are unclear.

Do not wait for the user to ask whether new work exists. If boundaries are stable but the ready
queue is thin, the upper planner should inspect code/docs and proactively mine same-lane deepening
candidates. Classify each candidate as implement-now, plan-first, ADR-first, wait-for-active-branch,
or defer; prefer crate-internal work with clear gates that avoids active hot files.

After assigning worker or lane terminals, the upper planner can keep working in read-only architecture
reconnaissance mode while they run. It may run scoped `$improve-codebase-architecture` sweeps for
the whole repo or individual lanes, check docs/code drift, and prepare the next-wave candidate
backlog. It must not rewrite active ledgers, change ADRs, assign extra implementation, or invalidate
running bundles without explicit approval.

## Too Many Workstreams

Treat too many workstreams as a status hygiene problem before changing layout:

- keep `docs/workstreams/<slug>/` flat and use metadata/indexes for lane grouping;
- inventory `WORKSTREAM.json` files before assigning terminals;
- close or split stale `active` workstreams before opening new ones;
- keep a short active queue per lane and defer the rest;
- avoid moving old workstream paths unless links and ADR references remain stable.

## Creating Terminals

The upper planner recommends terminals, worktree paths, branch names, creation commands, and prompts. It
may create approved worktrees or hand the commands to the user. Create terminals only after user
approval and only when the role has a clear scope and validation path.

Prefer one stable worktree per architecture lane, not one worktree per workstream. Reuse lane
worktrees across queued workstreams to reduce branch clutter, merge churn, and Rust `target/`
storage growth.

- Upper planner / main control terminal: discovers active work, owns sequencing, and assigns terminals.
- Architecture lane terminal: owns one capability area across queued workstreams.
- Worker terminal: owns one bounded task from `TODO.md`.
- Reviewer / verifier terminal: useful when output volume is high; otherwise the upper planner can
  run review and verification, or use `$integrate-lane-results` when completed output needs
  acceptance.
- Docs / next-version terminal: explores future plans but must not rewrite the active ledger.

When a worker reports `DONE`, the default next step is not "the worker reviews itself". The
integrator or upper planner either reviews/verifies in the current terminal or assigns a separate
reviewer/verifier terminal. The worker stands by for review fixes and waits for the next approved
task or bundle.

## Subagent Sidecars

Stable terminals and worktrees own durable lane execution. Explorer subagents are temporary sidecars
the upper planner may use for architecture review, code-aware lane planning, or independent
read-only questions. Their findings become planner evidence; they do not own planner state, accept work,
choose global sequencing, or perform side effects without approval.

Worker subagents may run only in `ASSIGN` / `EXECUTE` after the assignment gate passes:
`TASKS.jsonl` or `CAMPAIGNS.jsonl` must define the task, and scope, validation, stop conditions,
side-effect policy, and result marker must be explicit. Explorer subagents may run earlier, but only
as read-only evidence sources.

## Integration And Side Effects

The upper planner and integrator may analyze freely. Execute commits, merge, or sync only when the
current campaign policy pre-approves them; do not ask again for side effects that pass
`skills/engineering/dev-flow/references/side-effect-policy.md`. Otherwise ask before worktree
creation/deletion, branch operations, shared-scope edits, commits, merges, pushes, or related-repo
changes. After a result is inspected, integrate one lane branch at a time: review, verify with fresh
evidence, commit only approved changes, merge/sync in approved order, then update planner state and
the next Codex goal to set.

Commit at accepted task or bundle boundaries. Merge to main when another lane depends on the slice,
shared scopes changed, the bundle/workstream slice is complete, or divergence is becoming risk. Sync
main back into active lane worktrees after accepted merges and before new bundles or shared-scope
work.

## Cross-Repo Coordination

When work spans related repos, include each repo in the bundle: path, branch, dirty state, owned
scope, validation, and integration order. Stop when a related repo needs a user decision, ADR,
version bump, or release note.

## Architecture Lane Prompt

```text
Use $run-architecture-lane for the <lane> lane.
Set the current Codex goal to complete approved lane bundle <BUNDLE-ID> or lane campaign <CAMPAIGN-ID>.
Keep this terminal on the lane worktree, advance queued workstreams for this capability, and stop
when shared scopes, ADR changes, schema changes, or server contracts need upper-planner coordination.
Use the approved lane bundle or campaign as the maximum autonomous scope.
Recommend same-lane next actions only; the upper planner owns global sequencing.
```

## Worker Prompt

```text
Use $run-workstream-task to execute task <TASK-ID> from docs/workstreams/<slug>/TODO.md.
You are Worker <id>. You are not alone in the codebase.
Stay within the assigned file scope.
Read the assigned context manifest or task-specific context before editing.
Do not rewrite the global plan.
Do not revert user or other worker changes.
Report final status as DONE, DONE_WITH_CONCERNS, BLOCKED, or NEEDS_CONTEXT.
Report changed files, validation results, evidence updates, concerns, blockers, handoff notes, and a
recommended same-lane next action. Do not choose the global next task.
Include a `WORKSTREAM_RESULT:` marker.
Propose follow-ups or task splits instead of changing the workstream target state.
End by telling the user to return this report to the upper planner or integrator for review,
verification, and the next approved task or bundle.
```

## Reviewer Prompt

```text
Use $review-workstream to review completed worker tasks against the workstream DESIGN.md, TODO.md,
EVIDENCE_AND_GATES.md, repo AGENTS.md, and relevant ADRs. Report findings first, then residual risk
and missing gates. End with a `REVIEW_RESULT:` marker.
```

## Verifier Prompt

```text
Use $verify-rust-workstream to verify the reviewed task or lane with fresh command evidence before
the upper planner or integrator marks it complete. End with a `VERIFY_RESULT:` marker.
```

## Docs / Next-Version Prompt

```text
Use $grill-with-docs or $to-prd to prepare the next version plan.
Do not rewrite the active workstream target or TODO.md.
Produce ADR candidates, PRD/spec notes, prototype findings, or a proposed follow-on workstream.
```

## Integration Rule

Workers update their own task notes, evidence notes, and journal/handoff entries. The planner
integrates results into global task order, owner assignment, milestone state, and closeout decisions.

## Stop Conditions

Stop parallel execution and return to upper-planner or integration coordination when:

- two workers need the same file region,
- a task changes the workstream target state,
- a task reveals an ADR-level decision,
- validation cannot be run independently,
- or worker output conflicts with the workstream contract.

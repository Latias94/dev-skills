# Multi-Terminal Development

Chinese documentation: [../zh-CN/playbooks/multi-terminal-development.md](../zh-CN/playbooks/multi-terminal-development.md)

Use this playbook when one workstream needs multiple Codex terminals, or when a large project uses
one terminal per architecture lane.

If you are not sure the repo needs this much coordination, run `$audit-project-scale` first and
stay on `$dev-flow` for small or medium work.

## Terminal Map

```text
Terminal 1: Planner / PM
Terminal 2: Worker A
Terminal 3: Worker B
Terminal 4: Reviewer
Terminal 5: Verifier / closeout
Terminal 6: Docs / next-version planning
```

The planner can be a separate terminal or your main control terminal. It is the only terminal that
owns workstream creation/reuse, global sequencing, shared-scope decisions, and the task ledger.
Lane and worker terminals implement assigned bundles or tasks and report back.

For architecture-lane work, the planner owns cross-lane priorities and shared scopes. Lane terminals
own capability areas such as storage, transcode, playback, realtime, or admin.

Planner replies should use the current-terminal perspective. Start with what the planner should do
now, then list prompts to paste into other terminals. If the planner terminal will run review or
fresh verification, say so directly instead of saying "ask planner/reviewer".

## Planner State

For multi-worktree work, keep runtime facts in local `.codex/planner-state.local.json` or
`docs/local/PLANNER_STATE.md`. Track repo path, branch, head, dirty status, lane/workstream, active
task, lane goal bundle, context manifest, session refs, shared scopes, validation, and related
repositories. Commit examples and lane names only, not personal absolute paths.

Use `session_refs` as recovery pointers only. Planner decisions should come from workstream docs,
terminal reports, git state, and fresh verification, not raw chat history.

## Planner Discovery Prompt

Use this when you do not already know which workstream or lane should be active.

```text
Use $coordinate-workstream to inspect this repo and recommend a multi-terminal plan.
Do not assume there is a current workstream.
Read docs/architecture/LANES.md, WORKSTREAM_LINKS.md, docs/workstreams/*/WORKSTREAM.json, git
status, git worktree list, and documented related repositories.
Create or reuse workstreams only when the durable scope and gates are clear.
Use $plan-architecture-lane for selected architecture directions; it chooses planning depth and may
route to scoped $improve-codebase-architecture when lane seams or docs/code alignment are unclear.
Report candidate active workstreams or lanes, proposed lane goal bundles, Codex goals to set after
approval, recommended terminals, existing or new worktree paths, branch sync blockers, proposed
creation commands, terminal prompts, context manifests, and the first task each terminal should run.
Do not create new worktrees or branches until the user approves the plan.
```

## Known Workstream Planner Prompt

Use this when the workstream path is already known.

```text
Use $coordinate-workstream to coordinate docs/workstreams/<slug>.
Read WORKSTREAM.json, TODO.md, HANDOFF.md, EVIDENCE_AND_GATES.md, latest JOURNAL entries, and git
status. Assign only ready tasks with owners, file scopes, dependencies, and validation commands.
Integrate worker status reports, request review, request fresh verification, and decide whether to
continue, close, split follow-ons, or handoff.
```

Known architecture-lane planner prompt:

```text
Use $coordinate-workstream to coordinate architecture lanes.
Read docs/architecture/LANES.md, active WORKSTREAM.json files, git status, branches, and worktrees.
Approve which lane continues, which lane must sync main, and which lane is blocked by shared scopes.
Integrate completed workstreams one at a time after review and fresh verification.
```

## Result Inspection Prompt

Use this when a worker or lane terminal finished and the planner needs to decide what happens next.

```text
Use $coordinate-workstream to inspect the result in worktree <path>.
Read git status, git diff, changed file scope, related TODO.md, EVIDENCE_AND_GATES.md, HANDOFF.md,
and the terminal report. Use a session id only if the report or docs are missing.
Classify the result as ACCEPT_FOR_REVIEW, NEEDS_FIX, NEEDS_VERIFY, BLOCKED, or READY_FOR_NEXT_BUNDLE.
Then return the current planner action, review/verify owner, Codex goal to set, and pasteable
terminal prompts.
Do not let the worker choose the global next task.
```

## Lane Goal Bundles

A lane goal bundle is the planner-approved unit for long-running terminals. It should be bigger than
one mechanical edit and smaller than a whole architecture area.

Include:

- lane slug and worktree,
- one active workstream or a short same-lane queue,
- one to three ready task IDs,
- owned and shared scopes,
- context manifest such as `docs/workstreams/<slug>/CONTEXT.jsonl`,
- validation commands,
- stop conditions.

Use Codex goals only for a current bundle or one bounded task, not for an entire lane.

## Too Many Workstreams

Treat too many workstreams as a status hygiene problem before changing layout:

- keep `docs/workstreams/<slug>/` flat and use metadata/indexes for lane grouping;
- inventory `WORKSTREAM.json` files before assigning terminals;
- close or split stale `active` workstreams before opening new ones;
- keep a short active queue per lane and defer the rest;
- avoid moving old workstream paths unless links and ADR references remain stable.

## Creating Terminals

The planner recommends terminals, worktree paths, branch names, creation commands, and prompts. It
may create approved worktrees or hand the commands to the user. Create terminals only after user
approval and only when the role has a clear scope and validation path.

Prefer one stable worktree per architecture lane, not one worktree per workstream. Reuse lane
worktrees across queued workstreams to reduce branch clutter, merge churn, and Rust `target/`
storage growth.

- Planner / main control terminal: discovers active work, owns sequencing, and assigns terminals.
- Architecture lane terminal: owns one capability area across queued workstreams.
- Worker terminal: owns one bounded task from `TODO.md`.
- Reviewer / verifier terminal: useful when output volume is high; otherwise the planner can run
  review and verification.
- Docs / next-version terminal: explores future plans but must not rewrite the active ledger.

When a worker reports `DONE`, the default next step is not "the worker reviews itself". The planner
either reviews/verifies in the current terminal or assigns a separate reviewer/verifier terminal.
The worker stands by for review fixes and waits for the next planner-approved task or bundle.

## Integration And Side Effects

Planner may analyze freely, but must ask before worktree creation/deletion, branch operations,
shared-scope edits, commits, merges, pushes, or related-repo changes. After a result is inspected,
integrate one lane branch at a time: review, verify with fresh evidence, commit only approved
changes, merge/sync in planner-approved order, then update planner state and the next Codex goal to
set.

## Cross-Repo Coordination

When work spans related repos, include each repo in the bundle: path, branch, dirty state, owned
scope, validation, and integration order. Stop when a related repo needs a user decision, ADR,
version bump, or release note.

## Architecture Lane Prompt

```text
Use $run-architecture-lane for the <lane> lane.
Set the current Codex goal to complete planner-approved lane bundle <BUNDLE-ID>.
Keep this terminal on the lane worktree, advance queued workstreams for this capability, and stop
when shared scopes, ADR changes, schema changes, or server contracts need planner coordination.
Use the planner-approved lane goal bundle as the maximum autonomous scope.
Recommend same-lane next actions only; the planner owns global sequencing.
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
Propose follow-ups or task splits instead of changing the workstream target state.
End by telling the user to return this report to the planner for review, verification, and the next
approved task or bundle.
```

## Reviewer Prompt

```text
Use $review-workstream to review completed worker tasks against the workstream DESIGN.md, TODO.md,
EVIDENCE_AND_GATES.md, repo AGENTS.md, and relevant ADRs. Report findings first, then residual risk
and missing gates.
```

## Verifier Prompt

```text
Use $verify-rust-workstream to verify the reviewed task or lane with fresh command evidence before
the planner marks it complete.
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

Stop parallel execution and return to planner coordination when:

- two workers need the same file region,
- a task changes the workstream target state,
- a task reveals an ADR-level decision,
- validation cannot be run independently,
- or worker output conflicts with the workstream contract.

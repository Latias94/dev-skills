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
owns global sequencing, shared-scope decisions, and the task ledger.

For architecture-lane work, the planner owns cross-lane priorities and shared scopes. Lane terminals
own capability areas such as storage, transcode, playback, realtime, or admin.

## Planner Discovery Prompt

Use this when you do not already know which workstream or lane should be active.

```text
Use $coordinate-workstream to inspect this repo and recommend a multi-terminal plan.
Do not assume there is a current workstream.
Read docs/architecture/LANES.md, WORKSTREAM_LINKS.md, docs/workstreams/*/WORKSTREAM.json, git
status, git worktree list, and documented related repositories.
Report candidate active workstreams or lanes, recommended terminals, existing or new worktree paths,
branch sync blockers, and the first task each terminal should run.
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

## Creating Terminals

Create terminals only when the role has a clear scope and validation path:

- Planner / main control terminal: discovers active work, owns sequencing, and assigns terminals.
- Architecture lane terminal: owns one capability area across queued workstreams.
- Worker terminal: owns one bounded task from `TODO.md`.
- Reviewer / verifier terminal: useful when output volume is high; otherwise the planner can run
  review and verification.
- Docs / next-version terminal: explores future plans but must not rewrite the active ledger.

## Architecture Lane Prompt

```text
Use $run-architecture-lane for the <lane> lane.
Keep this terminal on the lane worktree, advance queued workstreams for this capability, and stop
when shared scopes, ADR changes, schema changes, or server contracts need planner coordination.
```

## Worker Prompt

```text
Use $run-workstream-task to execute task <TASK-ID> from docs/workstreams/<slug>/TODO.md.
You are Worker <id>. You are not alone in the codebase.
Stay within the assigned file scope.
Do not rewrite the global plan.
Do not revert user or other worker changes.
Report final status as DONE, DONE_WITH_CONCERNS, BLOCKED, or NEEDS_CONTEXT.
Report changed files, validation results, evidence updates, concerns, blockers, and handoff notes.
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

# Multi-Terminal Development

Chinese documentation: [../zh-CN/playbooks/multi-terminal-development.md](../zh-CN/playbooks/multi-terminal-development.md)

Use this playbook when one workstream needs multiple Codex terminals.

## Terminal Map

```text
Terminal 1: Planner / PM
Terminal 2: Worker A
Terminal 3: Worker B
Terminal 4: Reviewer
Terminal 5: Verifier / closeout
Terminal 6: Docs / next-version planning
```

The planner terminal is the only terminal that owns the global task ledger.

## Planner Prompt

```text
Use $coordinate-workstream to coordinate the active workstream.
Read WORKSTREAM.json, TODO.md, HANDOFF.md, EVIDENCE_AND_GATES.md, latest JOURNAL entries, and git
status. Assign only ready tasks with owners, file scopes, dependencies, and validation commands.
Integrate worker status reports, request review, request fresh verification, and decide whether to
continue, close, split follow-ons, or handoff.
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

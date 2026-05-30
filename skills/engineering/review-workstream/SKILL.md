---
name: review-workstream
description: >
  Reviews completed Rust workstream tasks along two axes: workstream compliance and code quality.
  Use when reviewing worker handoffs, task diffs, completed TODO.md items, branch changes, or
  deciding whether a workstream is ready for verification or closeout.
---

# Review Workstream

Use this from a reviewer or planner terminal. Review only; do not implement fixes here.

## Inputs

Require or infer:

- workstream path,
- task ID or review scope,
- diff range or changed files,
- relevant validation evidence.
- required context or `CONTEXT.jsonl` when present.

If the scope is unclear, ask the planner to pin it before reviewing.

## Read First

- `DESIGN.md`, `TODO.md`, `EVIDENCE_AND_GATES.md`, `WORKSTREAM.json`, `CONTEXT.jsonl` when present,
  and `HANDOFF.md`
- relevant ADRs and repo `AGENTS.md`
- `git status --short --branch`
- `git diff --name-status <base>...HEAD` and targeted diffs when a base is known

Do not reset, restore, checkout, stash, clean, or delete files during review.

## Axis 1: Workstream Compliance

Check whether the change satisfies the durable contract:

- task goal, done criteria, scope, dependencies, and validation command,
- `DESIGN.md` target state, non-goals, and milestones,
- accepted ADRs and repo-specific instructions,
- evidence updates in `EVIDENCE_AND_GATES.md`,
- no scope creep beyond the task or lane.

Report missing behavior, partial behavior, stale docs, missing evidence, and unapproved scope creep.

## Axis 2: Code Quality

Check implementation quality:

- Rust API shape, error handling, ownership, concurrency, and performance risks,
- test quality and whether tests prove behavior through public seams,
- module boundaries, naming, locality, and compatibility with existing patterns,
- docs and comments for behavior users or future agents need to know.

Do not duplicate machine checks unless the finding depends on a specific command output.

## Severity

- **Blocking**: unsafe to mark task complete or close the lane.
- **Important**: should be fixed before broader integration.
- **Minor**: can be follow-up if the planner agrees.
- **Missing gate**: implementation may be fine, but evidence is insufficient.

## Example

```text
Use $review-workstream to review task EMU-020 in docs/workstreams/emulator-mvp against its
workstream contract and the current branch diff.
```

## Output

Lead with findings, grouped by axis:

- `Workstream Compliance`
- `Code Quality`
- `Missing Gates`
- `Residual Risk`

For each finding include severity, file/path when relevant, the contract being violated, and the
required next action. If no blocking findings remain, say whether `$verify-rust-workstream` should
run next.

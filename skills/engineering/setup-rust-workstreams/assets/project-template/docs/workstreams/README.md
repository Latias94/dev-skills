# Workstreams

This directory contains durable engineering lanes: design notes, task ledgers, milestones, evidence
gates, audits, and closeout records.

Workstreams are not chat logs. They are the project memory for substantial changes.

## When To Create A Workstream

Create a workstream when the change has:

- a durable product or architecture goal,
- meaningful scope boundaries,
- multiple executable slices,
- validation gates,
- and a closeout condition.

Do not create a workstream for every small task.

## Standard Layout

```text
docs/workstreams/<slug>/
  DESIGN.md
  TODO.md
  CONTEXT.jsonl
  MILESTONES.md
  EVIDENCE_AND_GATES.md
  WORKSTREAM.json
  HANDOFF.md
  JOURNAL/
```

## Authority

If ADRs exist, accepted ADRs outrank workstreams. Workstream notes should link to ADRs rather than
restate contracts.

`CONTEXT.jsonl` is a short manifest of ADR, architecture, workstream, evidence, and research files
that lane terminals, workers, and reviewers should read. Do not list code files that workers are
about to modify.

## Status Hygiene

Use `WORKSTREAM.json` status values `draft`, `active`, `blocked`, and `closed`. Keep the active queue
short. Do not move historical workstreams into subfolders for architecture grouping; use
`lane_slug`, `architecture_refs`, `capability_tags`, and indexes instead.

## Gates

- Worker tasks report `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, or `NEEDS_CONTEXT`.
- Completed tasks are reviewed against workstream contract and code quality before acceptance.
- Completion claims require fresh verification evidence recorded in `EVIDENCE_AND_GATES.md`.

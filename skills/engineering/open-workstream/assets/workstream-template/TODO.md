# <Workstream Title> — TODO

Status: Draft
Last updated: YYYY-MM-DD

## M0 — Scope And Evidence Freeze

- [ ] WS-010 [owner=planner] [deps=none] [scope=docs/workstreams/<slug>]
  Goal: Freeze problem, target state, non-goals, and evidence anchors.
  Validation: DESIGN.md, MILESTONES.md, EVIDENCE_AND_GATES.md, WORKSTREAM.json, and CONTEXT.jsonl exist and agree.
  State: TASKS.jsonl entry WS-010 matches this task.
  Evidence: docs/workstreams/<slug>/DESIGN.md
  Context: docs/workstreams/<slug>/CONTEXT.jsonl
  Handoff: Upper planner owns this before workers start.

## M1 — First Vertical Proof

- [ ] WS-020 [owner=unassigned] [deps=WS-010] [scope=<crate-or-module>]
  Goal: Land the smallest independently validatable proof slice.
  Validation: cargo nextest run -p <package> <test-filter>
  Review: review-workstream before accepting completion.
  Evidence: <test-or-doc-path>
  Context: docs/workstreams/<slug>/CONTEXT.jsonl plus task-specific ADRs/research named by planner.
  Handoff: Final status must be DONE, DONE_WITH_CONCERNS, BLOCKED, or NEEDS_CONTEXT.
  State: TASKS.jsonl entry WS-020 records owner, scope, validation, evidence, and handoff status.

## M2 — Integration And Docs

- [ ] WS-030 [owner=unassigned] [deps=WS-020] [scope=docs,<crate-or-module>]
  Goal: Integrate the proof into the intended public or internal surface and update docs.
  Validation: cargo nextest run -p <package>
  Review: review-workstream for workstream compliance and code quality.
  Evidence: EVIDENCE_AND_GATES.md
  Context: docs/workstreams/<slug>/CONTEXT.jsonl
  Handoff: Split follow-on work if scope expands.
  State: TASKS.jsonl entry WS-030 records owner, scope, validation, evidence, and handoff status.

## M3 — Closeout

- [ ] WS-040 [owner=planner] [deps=WS-030] [scope=docs/workstreams/<slug>]
  Goal: Close the lane or create a narrower follow-on.
  Validation: verify-rust-workstream records fresh final gate evidence.
  Review: review-workstream has no blocking findings.
  Evidence: EVIDENCE_AND_GATES.md, WORKSTREAM.json
  Handoff: Summarize remaining risks in HANDOFF.md.
  State: TASKS.jsonl entry WS-040 is verified or accepted before closeout.

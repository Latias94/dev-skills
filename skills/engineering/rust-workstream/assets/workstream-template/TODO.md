# <Workstream Title> — TODO

Status: Draft
Last updated: YYYY-MM-DD

## M0 — Scope And Evidence Freeze

- [ ] WS-010 [owner=planner] [deps=none] [scope=docs/workstreams/<slug>]
  Goal: Freeze problem, target state, non-goals, and evidence anchors.
  Validation: DESIGN.md, MILESTONES.md, EVIDENCE_AND_GATES.md, WORKSTREAM.json exist and agree.
  Evidence: docs/workstreams/<slug>/DESIGN.md
  Handoff: Planner owns this before workers start.

## M1 — First Vertical Proof

- [ ] WS-020 [owner=unassigned] [deps=WS-010] [scope=<crate-or-module>]
  Goal: Land the smallest independently validatable proof slice.
  Validation: cargo nextest run -p <package> <test-filter>
  Evidence: <test-or-doc-path>
  Handoff: Record discovered follow-ups in this ledger, not only in chat.

## M2 — Integration And Docs

- [ ] WS-030 [owner=unassigned] [deps=WS-020] [scope=docs,<crate-or-module>]
  Goal: Integrate the proof into the intended public or internal surface and update docs.
  Validation: cargo nextest run -p <package>
  Evidence: EVIDENCE_AND_GATES.md
  Handoff: Split follow-on work if scope expands.

## M3 — Closeout

- [ ] WS-040 [owner=planner] [deps=WS-030] [scope=docs/workstreams/<slug>]
  Goal: Close the lane or create a narrower follow-on.
  Validation: closeout note and final gate set recorded.
  Evidence: EVIDENCE_AND_GATES.md, WORKSTREAM.json
  Handoff: Summarize remaining risks in HANDOFF.md.

---
name: close-workstream
description: >
  Close or split a Rust workstream after implementation. Use when the lane appears done, when
  evidence and gates need finalization, when deciding whether remaining work is a follow-on, or when
  updating MILESTONES.md, EVIDENCE_AND_GATES.md, WORKSTREAM.json, HANDOFF.md, and closeout notes.
---

# Close Workstream

Make completion explicit. Do not let lanes fade out.

## Check Before Closing

Read:

- `DESIGN.md`
- `TODO.md`
- `MILESTONES.md`
- `EVIDENCE_AND_GATES.md`
- `WORKSTREAM.json`
- relevant ADRs
- git status

Confirm:

- target state is met,
- task ledger is complete or remaining tasks are split/deferred,
- gate set proves the shipped behavior,
- docs teach the shipped behavior,
- no journal-only decisions remain.

## Close Or Split

- Close when the target state and gates are satisfied.
- Split a follow-on when remaining work has a new scope boundary.
- Keep the current lane open when the core target is incomplete.

## Write

Update:

- status notes in `DESIGN.md`, `TODO.md`, `MILESTONES.md`, and `EVIDENCE_AND_GATES.md`,
- `WORKSTREAM.json` status and continue policy,
- `HANDOFF.md` with residual risks or follow-ons,
- optional closeout audit if the repo convention uses one.

## Output

Report:

- final status,
- gates run or not run,
- evidence anchors,
- follow-ons,
- and remaining risks.

Do not commit without user confirmation.

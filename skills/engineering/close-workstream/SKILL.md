---
name: close-workstream
description: >
  Closes or splits a Rust workstream after implementation. Use when the lane appears done, when
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
- architecture refs or `docs/architecture/LANES.md` when the workstream belongs to a lane
- relevant ADRs
- latest `review-workstream` findings or review notes
- git status

Confirm:

- target state is met,
- task ledger is complete or remaining tasks are split/deferred,
- gate set proves the shipped behavior,
- fresh verification evidence exists for the closeout claim,
- docs teach the shipped behavior,
- architecture maps or lane registry reflect closeout/follow-ons when applicable,
- no journal-only decisions remain.

If review findings or required gates are missing, run `review-workstream` and
`verify-rust-workstream` before closing.

## Close Or Split

- Close when the target state and gates are satisfied.
- Split a follow-on when remaining work has a new scope boundary.
- Keep the current lane open when the core target is incomplete.

## Example

```text
Use $close-workstream to finalize docs/workstreams/emulator-mvp and split follow-ons.
```

## Write

Update:

- status notes in `DESIGN.md`, `TODO.md`, `MILESTONES.md`, and `EVIDENCE_AND_GATES.md`,
- `WORKSTREAM.json` status and continue policy,
- `HANDOFF.md` with residual risks or follow-ons,
- relevant architecture map or lane registry entries when the repo uses them,
- optional closeout audit if the repo convention uses one.

Use `status: "closed"` for completed, split, or intentionally stopped workstreams.

## Output

Report:

- final status,
- gates run or not run,
- evidence anchors,
- follow-ons,
- and remaining risks.

Do not commit without user confirmation.

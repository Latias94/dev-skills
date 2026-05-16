# <Workstream Title> — Milestones

Status: Draft
Last updated: YYYY-MM-DD

## M0 — Scope And Evidence Freeze

Exit criteria:

- Problem and target state are explicit.
- Non-goals are explicit.
- Relevant ADRs/docs/workstreams are linked.
- First proof target is chosen.

Primary evidence:

- `docs/workstreams/<slug>/DESIGN.md`
- `docs/workstreams/<slug>/TODO.md`

## M1 — First Vertical Proof

Exit criteria:

- One smallest proof slice lands.
- The slice is independently testable.
- Follow-up scope is recorded instead of silently widened.

Primary gates:

- `cargo nextest run -p <package> <test-filter>`

## M2 — Integration And Docs

Exit criteria:

- The proof is wired into the intended surface.
- Docs teach the shipped behavior.
- Evidence anchors are updated.

Primary gates:

- `cargo nextest run -p <package>`

## M3 — Closeout

Exit criteria:

- Gate set is recorded.
- Remaining work is either completed, deferred, or split into a follow-on.
- `WORKSTREAM.json` status is updated.

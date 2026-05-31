# Lane Deepening Backlog

Use this when the user wants one sub-architecture to keep maturing over many sessions, such as
storage, transcode, playback, realtime, admin, or addons.

## Core Rule

Durable ambition belongs in lane architecture docs and workstream queues, not in a Codex goal.
Codex goals should execute one bounded task, diagnosis loop, refactor milestone, or planner-approved
lane bundle. They should not represent "make this lane mature".

## Durable State

Prefer updating existing lane docs such as `docs/architecture/LANES.md` or
`docs/architecture/<lane>.md`. If no lane roadmap exists, propose
`docs/architecture/<lane>-roadmap.md` before creating many workstreams.

Track:

- current architecture state and constraints,
- target maturity level and reference product expectations,
- capability gaps and risks,
- active, draft, deferred, and blocked workstreams,
- next lane goal bundles,
- validation ladder from targeted tests to broader integration gates,
- shared scopes and lanes that must be serialized,
- related repo responsibilities.

## Refresh Loop

When the active queue is nearly empty or the tasks are too small:

1. Re-read lane docs, active workstreams, code seams, and validation evidence.
2. Run a source coverage audit.
3. Use code-aware planning or scoped `improve-codebase-architecture` when target state, seams, or
   docs/code alignment are unclear.
4. Add or revise the lane backlog before assigning new work.
5. Open or reuse workstreams only for durable slices with clear gates.

## Goal Sizing

For long-running terminals, combine adjacent ready same-lane tasks into one bundle when scopes,
dependencies, and validation are clear. Aim for a coherent 45-120 minute autonomous bundle, but keep
explicit stop conditions and never include unreviewed ADR changes, unclear shared scopes, or
cross-lane edits.

When the requirement and future direction are already clear, plan deeper than the next bundle. Build
an ordered lane campaign with several ready bundles or workstreams so a lane terminal can run longer
with less user intervention. Use `grill-with-docs` first when future requirements are not crisp
enough.

A campaign is ready only when source coverage has no required `MISSING` or `BLOCKED` items, each
step has validation and evidence updates, and auto-advance/stop rules are explicit. Keep the
campaign in lane docs, planner state, or workstream docs; the Codex goal references the campaign but
does not replace it.

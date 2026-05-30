# Lane Goal Bundles

A lane goal bundle is the planner-approved unit for long-running terminal work. It is larger than a
tiny task and smaller than a whole architecture area.

Good bundle:

- one lane and one stable worktree,
- one active workstream or a short same-lane queue,
- one to three ready task IDs,
- disjoint owned scopes,
- explicit shared scopes that require planner approval,
- one validation path the lane terminal can run,
- context manifest path,
- clear stop conditions.

Bad bundle:

- "refactor storage" with no task IDs,
- a whole subsystem with no closeout gate,
- cross-lane shared crate changes without planner serialization,
- tasks whose requirements are still being grilled.

If the user wants a Codex goal, set it for the bundle or the next task only. Do not set a goal for
an unbounded architecture lane.

Planner output should include the exact goal text to set for each approved terminal, such as
`Complete lane bundle storage-YYYYMMDD-01`.

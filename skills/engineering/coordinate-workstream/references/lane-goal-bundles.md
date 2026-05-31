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

When a bundle or next task is ready for longer autonomous work, recommend a bounded Codex goal and
ask whether to set it. Do not set a goal for an unbounded architecture lane.

Planner output should include the exact goal text to set for each approved terminal, such as
`Complete lane bundle storage-YYYYMMDD-01`.

If bundles routinely finish too quickly, combine adjacent ready same-lane tasks into a larger bundle
only when they share a lane, have clear dependencies, avoid shared-scope ambiguity, and use one
validation path. A good long-running bundle is usually a coherent 45-120 minute slice. Keep the
long-term lane ambition in architecture docs or a lane deepening backlog, not in the Codex goal.

## Lane Campaigns

When requirements, docs, task ledgers, and validation are strong enough, the planner may approve an
autonomous lane campaign: an ordered sequence of lane bundles or same-lane workstreams that one
terminal may run under one longer Codex goal.

A campaign must include:

- campaign ID and lane/worktree,
- ordered bundle/workstream queue,
- per-step task IDs, owned scopes, validation, and evidence updates,
- auto-advance rule, such as "continue only when this step's gates pass",
- checkpoints the terminal reports after each step,
- stop conditions for failed gates, missing context, shared scopes, ADR/schema/contract changes,
  dirty unrelated files, or unapproved side effects.

The planner may ask for upfront approval for specific side effects inside the campaign, such as
task-boundary commits. Without that approval, the terminal stops before commit, merge, push,
worktree, branch, or shared-scope operations.

Example goal text:

```text
Execute planner-approved lane campaign storage-YYYYMMDD-01 through bundles B1-B4 in order. Auto-advance only when each step's validation passes and evidence is updated. Stop before shared scopes, ADR/schema/contract changes, failed gates, missing context, or unapproved side effects.
```

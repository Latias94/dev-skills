# Run Envelope

Use a run envelope when a goal should continue beyond a short interactive edit.

The run envelope is not a separate workflow. It is the boundary around one goal cycle: what the agent may do, when it must stop, and what evidence it must leave.

## Model

```text
north star -> project memory -> goal contract -> run envelope -> loom lane map -> evidence -> memory update
```

## Fields

```text
mode: plan_only | bounded_execute | autonomous_queue | refactor_pulse
active_memory:
phase:
goal:
done_when:
allowed_changes:
forbidden_changes:
subagent_policy:
worktree_policy:
commit_policy:
progression_rule:
stop_rule:
context_manifest:
verification:
evidence_required:
finish_gate:
handoff_to:
```

## Modes

- `plan_only`: clarify direction, update memory, no implementation.
- `bounded_execute`: execute one approved goal, then stop for review.
- `autonomous_queue`: continue through pre-approved child goals while each goal passes its checks.
- `refactor_pulse`: improve architecture or tests within a defined module boundary before more feature work.

## Rules

- Prefer one primary implementation lane plus read-only research/check lanes unless multiple writers have disjoint ownership.
- Treat public API, schema, generated contracts, ADRs, root manifests, and repo instructions as escalation surfaces unless explicitly included.
- Convert broad uncertainty into research lanes instead of expanding implementation scope.
- Stop after repeated failure of the same class unless the plan changes.
- Separate completed verified work from partial work, research, and recommendations.
- Keep active memory, code state, and final report consistent before closing the run.
- Default `subagent_policy` to `loom_decides_after_lane_map`.
- Default `worktree_policy` to sibling worktrees shaped as `../<repo-name>-worktrees/<goal-slug>/<lane-id>`.
- Default `commit_policy` to `allowed_after_green` for worker lanes when the user approved bounded or autonomous execution.
- Never push, merge, amend, or rewrite shared history unless explicitly approved.
- If repo instructions forbid self-commit, report the conflict and use the stricter rule.

## Evidence

Every run envelope should leave enough evidence for the next session to answer:

```text
what goal was active?
what changed?
what was verified?
what was committed?
what stopped or failed?
what memory was updated?
what is the next recommended decision?
```

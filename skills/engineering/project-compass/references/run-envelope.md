# Run Envelope Adapter

Use a run envelope only to summarize local constraints for CE or Loom fallback.

The run envelope is not a workflow and does not replace CE plans. It is a compact boundary: what the
agent may do, when it must stop, and what evidence it must leave.

## Model

```text
CE strategy/brainstorm/plan -> local run envelope -> ce-work or loom fallback -> evidence -> CE/repo memory update
```

## Fields

```text
mode: plan_only | bounded_execute | autonomous_queue | refactor_pulse
active_memory:
phase:
goal:
done_when:
success_metrics:
allowed_changes:
forbidden_changes:
subagent_policy:
worktree_policy:
commit_policy:
progression_rule:
stop_rule:
context_manifest:
verification:
verification_ladder:
autonomy_watch:
evidence_required:
finish_gate:
handoff_to: ce-strategy | ce-brainstorm | ce-plan | ce-work | ce-code-review | ce-compound | loom-fallback
```

## Modes

- `plan_only`: clarify direction through CE, no implementation.
- `bounded_execute`: execute one approved CE plan or fallback goal, then stop for review.
- `autonomous_queue`: continue only when the user has explicitly approved a CE or fallback queue.
- `refactor_pulse`: improve architecture or tests within a defined module boundary before more feature work.

## Rules

- Before delegating a large chunk of work, define `done_when`, `success_metrics`, and the cheapest
  reliable `verification_ladder`. If success cannot be verified, keep the run in CE planning,
  research, or architecture-first mode.
- Prefer one primary implementation lane plus read-only research/check lanes unless multiple writers have disjoint ownership.
- Treat public API, schema, generated contracts, ADRs, root manifests, and repo instructions as escalation surfaces unless explicitly included.
- Convert broad uncertainty into research lanes instead of expanding implementation scope.
- For `autonomous_queue` or long-running `bounded_execute`, define `autonomy_watch`: who checks
  execution drift, who checks direction drift, what evidence they read, and when they interrupt.
- Stop after repeated failure of the same class unless the plan changes.
- Separate completed verified work from partial work, research, and recommendations.
- Keep active memory, code state, and final report consistent before closing the run.
- Default `subagent_policy` to `ce_owns_unless_fallback`.
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
what CE artifact or repo memory was updated?
what correction should update a skill, repo instruction, test, or checklist?
what is the next recommended decision?
```

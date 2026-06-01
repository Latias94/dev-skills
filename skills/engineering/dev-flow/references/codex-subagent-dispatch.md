# Codex Subagent Dispatch

Use this when Codex has native subagent tools available. Subagents add parallel attention; they do
not replace durable repo state.

## Role Mapping

| Program state | Subagent type | Purpose | Writes |
| --- | --- | --- | --- |
| `DISCOVERY` | `explorer` | answer bounded codebase or docs questions | none |
| `RECON` | `explorer` | prepare next-wave candidates while workers run | none |
| `EXECUTE` | `worker` | implement one approved task, bundle step, or campaign step | assigned scope only |
| `REVIEW` | `explorer` or reviewer terminal | independent contract/code review | none unless explicitly assigned docs notes |
| `VERIFY` | main terminal or verifier terminal | run fresh gates and record evidence | evidence only |
| `INTEGRATE` | main terminal | reconcile state, commit, sync, merge when approved | integration state only |

Do not spawn workers in `DISCOVERY`, `SHAPE`, or `PLAN`. Do not spawn implementation workers when
`Implementation Horizon: 0`.

## Spawn Preconditions

Before a worker subagent is spawned, all must be true:

- `TASKS.jsonl` or an approved campaign defines the task ID and status.
- `CAMPAIGNS.jsonl` defines auto-advance order when more than one task may run.
- owned scope, shared scope, validation, stop conditions, and side-effect policy are explicit.
- worktree/branch identity is known.
- dirty unrelated files are classified.
- the subagent prompt includes the required result marker from `agent-contracts.md`.

Explorer subagents may run earlier, but their output is evidence for the planner, not an assignment.

## Dispatch Prompt Fields

Every worker prompt includes:

```text
Role:
Program state:
Task or campaign:
Owned scope:
Forbidden/shared scope:
Required context:
Validation:
Stop conditions:
Side-effect policy:
Result marker:
Return path:
```

The prompt must say: "You are not alone in the codebase." It must also forbid choosing the global
next task.

## Integration Rule

Subagent output is never accepted directly. The main terminal reconstructs the result from git,
docs, task state, campaign state, evidence, and the final marker, then routes to review and fresh
verification.

## Parallelism Rule

Parallel workers are allowed only when their owned scopes are disjoint or explicitly serialized by a
campaign. Shared scopes, public contracts, ADR changes, schema changes, and generated contract
updates stay serialized unless the planner records an approved coordination plan.

## Failure Modes

Stop using worker subagents and return to planner state when:

- worker scope expands beyond the approved task,
- result marker is missing or inconsistent,
- gates fail and the revision loop stalls,
- the worker modifies shared scope without approval,
- conflicts appear between repo artifacts and worker claims,
- context budget is exhausted before integration evidence is reconstructed.

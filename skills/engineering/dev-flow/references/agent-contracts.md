# Agent Contracts

Use this when assigning a terminal, reading a worker report, or parsing session tails.

Every role returns a small structured marker. Narrative is allowed after the marker, but the marker
is the contract the integrator can parse.

## Status Vocabulary

Worker and lane terminals:

- `DONE`: assigned implementation and task-local validation completed.
- `DONE_WITH_CONCERNS`: assigned implementation completed, but named concerns remain.
- `BLOCKED`: cannot continue without a task split, design change, failed dependency, or external input.
- `NEEDS_CONTEXT`: required context is missing, stale, contradictory, or inaccessible.

Review terminals:

- `PASS`: no blocking or important review findings.
- `PASS_WITH_CONCERNS`: acceptable only if the integrator records follow-ups or residual risk.
- `FAIL`: blocking findings or unapproved scope changes exist.
- `NEEDS_SCOPE`: reviewer cannot identify the approved diff, task, or contract.

Verification terminals:

- `PASS`: fresh commands prove the claim.
- `FAIL`: commands failed or disprove the claim.
- `INCONCLUSIVE`: required gates could not be run and the reason is recorded.

Integration terminals:

- `ACCEPTED`: review, verification, evidence, and state reconciliation passed.
- `NEEDS_FIX`: worker or lane must revise within the existing assignment.
- `BLOCKED_DECISION`: user or upper-planner decision is required.
- `READY_FOR_NEXT_BUNDLE`: accepted output is ready and the lane may receive the next approved unit.

## Worker Marker

```text
WORKSTREAM_RESULT:
status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
lane: <lane-or-none>
workstream: docs/workstreams/<slug>
task_ids: <ids>
campaign_id: <id-or-none>
branch: <branch>
worktree: <path>
changed_files: <paths-or-none>
validation: <commands and result summary>
evidence_updates: <paths-or-none>
concerns: <concerns-or-none>
next_action: <advisory only>
```

## Review Marker

```text
REVIEW_RESULT:
status: PASS | PASS_WITH_CONCERNS | FAIL | NEEDS_SCOPE
scope: <task/campaign/diff>
blocking_findings: <count and short list>
important_findings: <count and short list>
missing_gates: <gates-or-none>
required_next_action: <fix/verify/integrate/escalate>
```

## Verify Marker

```text
VERIFY_RESULT:
status: PASS | FAIL | INCONCLUSIVE
claim: <claim verified>
commands: <commands with exit result>
evidence_path: <path updated>
skipped_gates: <gates and reasons>
required_next_action: <integrate/fix/escalate>
```

## Integration Marker

```text
INTEGRATION_RESULT:
status: ACCEPTED | NEEDS_FIX | BLOCKED_DECISION | READY_FOR_NEXT_BUNDLE
scope: <task/campaign/lane>
accepted_files: <paths-or-none>
state_updates: <TODO/TASKS/CAMPAIGNS/evidence updates>
side_effects: <commits/sync/merge/push-or-none>
next_owner: <planner/lane/worker/user>
next_action: <bounded next step>
```

## Parsing Rule

If a marker is missing or internally inconsistent, classify the result as `NEEDS_SCOPE` or
`NEEDS_CONTEXT` before accepting it. Do not accept a plain `DONE` sentence as completion.

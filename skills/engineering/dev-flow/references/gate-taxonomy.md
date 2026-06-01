# Gate Taxonomy

Use this when defining assignment readiness, review loops, verification gates, or stop conditions.

## Gate Types

- Pre-flight gate: must pass before implementation assignment.
- Revision gate: runs after review or verification fails and bounds the fix loop.
- Escalation gate: routes a decision to the user or upper planner.
- Abort gate: stops unsafe, destructive, or unbounded execution.

## Pre-Flight Gates

Before `ASSIGN`, confirm:

- approved scope, owner, and branch/worktree,
- `TODO.md`, `TASKS.jsonl`, and `CAMPAIGNS.jsonl` agreement,
- context manifest exists when context is non-trivial,
- validation command exists and is runnable,
- worktree status and unrelated changes are classified,
- side-effect policy and stop conditions are explicit.

Failure leaves the program in `DISCOVERY`, `PLAN`, or `DECISION`; do not start implementation.

## Revision Gates

Use a bounded check-revise-escalate loop:

1. reviewer or verifier records structured issues,
2. the original worker revises inside the approved scope,
3. reviewer or verifier reruns only the relevant checks,
4. the issue count must decrease or severity must drop.

Default cap: three revision attempts for the same assignment. Escalate when the same blocker repeats,
issue count stalls, or the fix requires new scope.

## Escalation Gates

Escalate before:

- ADR, schema, public API, migration, security, or data-loss decisions,
- shared-scope changes across lanes,
- related-repo changes,
- commits, sync, merge, worktree creation, or push not covered by campaign policy,
- failed gates that need scope reduction or product tradeoffs.

## Abort Gates

Abort the current assignment when:

- the worker is outside approved scope,
- validation cannot be made meaningful,
- destructive commands are requested without explicit approval,
- dirty unrelated files cannot be isolated,
- branch/worktree identity is ambiguous,
- the assignment becomes an unbounded refactor.

## Gate Record

Record gate outcomes in `EVIDENCE_AND_GATES.md` or the relevant machine-readable state:

```text
Gate:
Scope:
Command or check:
Result:
What it proves:
Skipped broader gates:
Next action:
```

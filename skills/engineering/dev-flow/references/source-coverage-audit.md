# Source Coverage Audit

Use this before turning a user goal into a workstream, task ledger, lane bundle, or long-running
Codex goal. The goal is to prove the plan is grounded in the right sources instead of chat memory.

## Sources

Audit only sources relevant to the requested scope:

- user goal, non-goals, and constraints,
- `CONTEXT.md`, `AGENTS.md`, and relevant ADRs,
- `docs/architecture/` lane maps and target-state docs,
- active workstream `DESIGN.md`, `TODO.md`, `WORKSTREAM.json`, `CONTEXT.jsonl`, `HANDOFF.md`,
- `EVIDENCE_AND_GATES.md` and known validation commands,
- code evidence from relevant crates/modules/tests,
- related repo docs/status when the work crosses repositories,
- subagent or research findings, treated as evidence until promoted into repo docs.

## Coverage States

- `COVERED`: source exists, was read, and supports the plan.
- `MISSING`: required source is absent or stale.
- `DEFERRED`: source is optional for the current slice and explicitly postponed.
- `BLOCKED`: missing source requires user, ADR, related repo, or product decision.
- `OUT_OF_SCOPE`: source is intentionally excluded by non-goals.

## Gate

Do not mark a workstream, lane bundle, or Codex goal ready when a required source is `MISSING` or
`BLOCKED`. Either read/update the source, ask for the decision, or route to
`improve-codebase-architecture`, `grill-with-docs`, or `open-workstream`.

## Output

Report a short coverage table: source, state, evidence path, impact, and required action. Keep it
small enough to act on; only expand sources that affect the current planning decision.

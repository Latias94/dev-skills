# Planner Rehearsal Notes — 2026-06-02

## Purpose

This note turns current script output into a planner-style rehearsal for the two real repositories
under `repo-ref/`.

The goal is not to pretend that a full interactive planner run already happened. The goal is to
check whether the current scripts and contracts are now strong enough to support a coherent planner
answer.

## Rehearsal: Nako

### Evidence read

- `program_status.py repo-ref/nako`
- existing repository baseline notes
- current findings note

### Observed planner signal

- `Operating Mode: READINESS`
- `Implementation Horizon: 1`
- one active ready workstream:
  `generated-artifact-bulk-metadata-apply`
- current task:
  `GABMA-020`
- lane:
  `library-metadata-control-plane`

### Expected planner-style answer

The planner should report that the repo is not in bootstrap or historical-audit mode. It has a
live queue with one assignable workstream and should recommend bounded assignment or workstream
resume, not global replanning.

### What this proves

The current system can now support a coherent answer of the form:

- current phase,
- `Operating Mode: READINESS`,
- `Implementation Horizon: 1`,
- next safe route: resume or assign bounded work from the active queue.

### What still needs work

- the planner does not yet synthesize this into a richer user-facing recommendation automatically
- the scripts do not yet explain whether `GABMA-020` is the best next task or merely the current one

## Rehearsal: Hajimi

### Evidence read

- `program_status.py repo-ref/hajimi`
- existing repository baseline notes
- current findings note

### Observed planner signal

- `Operating Mode: AUDIT`
- `Implementation Horizon: 0`
- no active workstreams
- only historical workstream corpus in current snapshot

### Expected planner-style answer

The planner should not sound blocked or confused. It should explain that:

- there is no active queue in the current snapshot,
- this is an audit baseline,
- next move is either to inspect whether a new workstream should be opened or to review historical
  quality depending on the user's intent.

### What this proves

The current system can now support a coherent zero-horizon answer without implying that active work
is broken.

### What still needs work

- no dedicated audit summary script yet
- planner still needs stronger natural-language examples for “history only” situations

Update:

- `audit_summary.py` now exists and groups historical drift by pattern
- a richer `nako` planner rehearsal is recorded in
  `docs/evals/results/2026-06-02-nako-planner-rehearsal-v2.md`
- `planner_payload.py` now exists as a unified read-only planner entrypoint
- `hajimi` audit-mode output is summarized in
  `docs/evals/results/2026-06-02-hajimi-audit-summary-notes.md`

## Interim Conclusion

The current refactors have moved `dev-skills` from:

- “script output exists but planner language is ambiguous”

to:

- “script output and planner language now share a usable readiness/audit model”

That is enough to justify continuing refinement instead of a foundational redesign.

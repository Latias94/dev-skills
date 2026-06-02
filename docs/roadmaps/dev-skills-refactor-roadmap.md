# Dev Skills Refactor Roadmap

## Status

Working draft based on comparison against Trellis and Matt skills, plus real-repo inspection of
`repo-ref/nako` and `repo-ref/hajimi`.

## Problem Statement

`dev-skills` already has strong architectural governance and artifact modeling for large Rust
projects, but it still relies too heavily on prompt compliance.

We need to preserve:

- project-owned truth in ADRs, architecture docs, and workstreams,
- composability with Matt-style local engineering skills,
- review and verification discipline,
- worktree and side-effect safety.

We need to improve:

- runtime phase guidance,
- artifact drift detection,
- real-repo evaluation,
- and workflow scale sharpness.

## Refactor Themes

### Theme 1: Runtime breadcrumb for Dev Skills

Borrow the useful part of Trellis without adopting Trellis task truth.

Add a lightweight runtime representation for:

- current orchestration phase,
- active workstream or bundle,
- required next action,
- required evidence freshness,
- stop conditions,
- blocked reason when applicable.

This should be derived from project artifacts, not replace them.

### Theme 2: Stronger orchestration validation

Expand validation beyond current planner-state checks.

Potential checks:

- active workstream missing required files,
- `TODO.md` and `TASKS.jsonl` disagreement,
- campaign marked ready but no stop conditions or validation ladder,
- completion claims without fresh verification evidence,
- handoff-only decisions that should have landed in durable docs.

### Theme 3: Real-repo scenario harness

Build a repeatable evaluation workflow for:

- `repo-ref/nako`
- `repo-ref/hajimi`
- future large Rust references

Scenarios should test:

- route choice,
- context loading,
- evidence discipline,
- campaign readiness,
- operator friction.

### Theme 4: Ceremony budget

Clarify the smallest justified workflow shape for each class of work.

This theme should reduce:

- unnecessary workstream creation,
- unnecessary upper-planner escalation,
- unnecessary user questioning when repo evidence already answers the question.

### Theme 5: Sharper entrypoint outputs

User-facing orchestrator skills should always report:

- current phase,
- chosen route,
- evidence used,
- what is safe to do now,
- which side effects are still pending approval,
- exact next prompt or bounded goal when execution becomes ready.

## First Iteration Targets

1. Add analysis and evaluation docs to the repo.
2. Audit whether current skills already contain enough structure for a runtime breadcrumb.
3. Identify the minimum file/schema addition needed for stronger state checks.
4. Add one or more scripts/tests that fail on obvious orchestration drift.
5. Run at least one documented scenario each on `nako` and `hajimi`.

## Decision Rules

### Keep

- artifact authority order,
- composition with Matt skills,
- workstream and lane abstractions,
- hard review and fresh verification,
- Rust-first validation discipline.

### Change

- anything that depends on memory instead of machine-checkable state,
- anything that causes repeated ambiguous phase selection,
- anything that makes medium work more ceremonial than useful,
- anything that lets “done” bypass verification freshness.

### Do Not Introduce

- a second source of truth that competes with ADRs or workstream docs,
- Trellis-style task ownership as the universal top-level abstraction,
- mandatory heavy process for small direct tasks.

## Validation Repositories

### `repo-ref/nako`

Why it matters:

- large multi-surface Rust workspace,
- explicit architecture docs and lanes,
- existing workstream structure,
- real deployment and validation surface.

Questions it can answer:

- does `dev-skills` choose planning depth correctly?
- does lane planning actually help?
- does the workflow stay usable on a product-scale repo?

### `repo-ref/hajimi`

Why it matters:

- dense ADR set,
- many real workstreams,
- explicit architecture boundary work,
- already aligned with this style of governance.

Questions it can answer:

- are current skill abstractions actually sufficient?
- where does runtime ambiguity still leak through?
- which validations should become scripts instead of prompt instructions?

## Exit Criteria For This Refactor Program

This refactor program is in good shape when:

- route choice is predictably correct on real repos,
- active-phase ambiguity is substantially reduced,
- artifact drift is caught automatically more often,
- operator burden is clearly lower than the current state,
- and the repo can explain, with evidence, why it is not simply “Trellis but bigger”.

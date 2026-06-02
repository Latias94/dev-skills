# Medium Fixture Candidate Audit

## Purpose

This note records which existing repositories under `repo-ref/` are the best candidates for the
next evaluation axis:

- medium-task over-escalation

The goal is to prefer a real repository over a synthetic fixture whenever possible.

## Candidates Checked

Repositories present under `repo-ref/` during this pass:

- `codex`
- `gsd-core`
- `hajimi`
- `nako`
- `skills`
- `superpowers`
- `Trellis`

## Screening Heuristic

A good medium-task fixture should have most of these properties:

- real repository, not an invented micro-fixture
- `AGENTS.md` and `CONTEXT.md` present
- enough architecture language to make the workflow meaningful
- no heavy architecture-lane substrate
- few or no durable workstreams
- a plausible bounded bug/feature request where planner escalation would look excessive

## Findings

### `repo-ref/skills`

Best current candidate.

Why:

- has `CONTEXT.md`
- has skill/domain language already oriented around sharp engineering tasks
- repository ethos explicitly resists process ownership and over-orchestration
- no visible large workstream substrate or lane system in the same style as `nako` / `hajimi`
- naturally fits prompts like:
  - fix a skill bug
  - adjust one skill contract
  - refine one docs/codepath loop

Risk:

- does not currently mirror the exact `dev-skills` workstream substrate, so some planner-specific
  checks may be inapplicable

Verdict:

- use as the first real candidate for a medium-task over-escalation scenario

### `repo-ref/codex`

Possible secondary candidate.

Why:

- real large codebase with many small subdomains
- could support a narrow prompt against one crate/module

Risk:

- overall repository is large enough that planner-aware caution can still be rational
- without a carefully chosen sub-area, the signal would be muddy

Verdict:

- good fallback if a narrower `skills` scenario proves too trivial

### `repo-ref/gsd-core`

Poor candidate for this axis.

Why:

- already very workflow-heavy
- explicit planning/workstream substrate is part of the product itself
- hard to distinguish “over-escalation” from normal repository operating mode

Verdict:

- avoid for the first medium-task restraint scenario

### `repo-ref/nako` and `repo-ref/hajimi`

Not suitable for medium-task restraint validation.

Why:

- both are already the large-repo baselines
- planner-aware behavior is often justified simply because of repo scale and substrate complexity

Verdict:

- keep them for large-repo planner/worker boundary tests only

### `repo-ref/superpowers` and `repo-ref/Trellis`

Possible later comparison targets, not first-choice medium fixtures.

Why:

- both are valuable for workflow comparison
- but less directly aligned with the current `dev-skills` substrate evaluation than `skills`

Verdict:

- defer for now

## Recommendation

The next runnable medium-task scenario should target:

- `repo-ref/skills`

Recommended shape:

- a bounded prompt about changing or debugging one engineering skill
- expected scale: `direct` or `workstream`
- failure mode: `plan-engineering-program` or similar heavy orchestration would count as
  over-escalation

## Follow-Up

If `repo-ref/skills` still proves too broad or too unlike `dev-skills` after one trial run:

1. try a carefully bounded `repo-ref/codex` subdomain prompt, or
2. add a dedicated medium fixture under `repo-ref/`

## Update After First Trial

The first runnable medium scenario was tested against `repo-ref/skills` with:

- expected scale: `direct`
- expected route: `audit-project-scale`
- intent: stay light, avoid planner/lane/program ceremony

Observed result:

- route stayed light enough to avoid `plan-engineering-program`
- but the workflow stopped at read-only discovery instead of naturally downshifting into a sharper
  implementation-oriented route such as `tdd` or `diagnose`

Implication:

- `repo-ref/skills` is still a valid medium-task restraint candidate
- but the current `dev-skills` routing layer is conservative on repos without explicit workstream
  substrate
- the next iteration should test whether `dev-flow` or a dedicated medium-task router can bridge
  from `audit-project-scale` into a sharper engineering skill without demanding planner-heavy
  artifacts first

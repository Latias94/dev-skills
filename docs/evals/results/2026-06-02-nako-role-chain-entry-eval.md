# Nako Role-Chain Entry Eval — 2026-06-02

## Goal

Validate whether real subagents keep the same active unit after planner handoff on `repo-ref/nako`.

This eval covers role-entry behavior only.
It does not perform implementation, review, verification, or integration.

## Active Unit

All roles were grounded on the same active unit:

- workstream:
  `generated-artifact-bulk-metadata-apply`
- task:
  `GABMA-020`
- campaign:
  `GABMA-20260601-01`

Current repo state before these checks:

- `Operating Mode: READINESS`
- `Implementation Horizon: 1`
- recommended route:
  `run-workstream-task`

## Worker Entry

Result: `PASS`

Observed behavior:

- confirmed it would execute only `GABMA-020`
- kept the same workstream and campaign
- bound itself to the required context list
- named stop conditions:
  - failed gate
  - scope drift
  - ADR/schema/public-contract drift
  - bulk mutation implementation
  - generated client drift
  - dirty unrelated files
  - missing context
  - unapproved push
- did not choose a different task, workstream, or lane

Why it passes:

- worker entry stayed bounded before implementation began
- response shape matched a real worker start rather than a broad analysis report

## Reviewer Entry

Result: `PASS`

Observed behavior:

- confirmed it would review only `GABMA-020`
- rejected scope widening into persistence, execution, route exposure, Web work, closeout, or follow-on tasks
- required reviewable evidence before proceeding:
  - `WORKSTREAM_RESULT:`
  - changed files
  - base/head or diff
  - implementation summary
  - validation output
  - evidence/doc updates
  - concerns
  - `git status --short --branch`
- did not pretend to review without diff/evidence

Why it passes:

- reviewer preserved the active-unit boundary
- reviewer refused false completion when inputs were insufficient

## Verifier Entry

Result: `PASS`

Observed behavior:

- confirmed it would verify only `GABMA-020`
- required fresh command evidence before pass/fail or merge-readiness
- refused to accept worker prose `DONE` as evidence
- checked that the result still belonged to the redaction-safe, read-only bulk apply-plan contract
- did not verify a different task, workstream, or lane

Why it passes:

- verifier preserved the active-unit boundary
- verifier enforced fresh evidence rather than trusting chat claims

## Overall Result

Result: `PASS`

The role chain now has behavior evidence for:

1. planner bounded assignment
2. worker bounded entry
3. reviewer bounded entry
4. verifier bounded entry

This is stronger than prompt or script rehearsal alone.
The first four role boundaries all kept the same active unit and did not drift into global planning
or unrelated workstreams.

## Remaining Unproven Layer

The following remain unproven:

- real worker implementation quality
- reviewer behavior against a real diff
- verifier behavior against real command output
- integrator evidence reconstruction after actual worker/review/verify outputs

The next useful experiment is either:

1. integrator-entry behavior with synthetic but explicit worker/review/verify result markers, or
2. a tiny real implementation attempt for `GABMA-020` followed by review and verification.

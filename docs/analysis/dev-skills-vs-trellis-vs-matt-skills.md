# Dev Skills vs Trellis vs Matt Skills

## Purpose

This document captures the architectural comparison between:

- `dev-skills` in this repository,
- `repo-ref/Trellis`,
- `repo-ref/skills` (Matt Pocock skills).

The goal is not to crown a winner. The goal is to clarify:

1. which problem each system is actually solving,
2. where `dev-skills` is directionally correct,
3. where `dev-skills` is still too soft at runtime,
4. which refactors should be validated against real repositories.

## Short Verdict

`dev-skills` is directionally right for large Rust programs with long-lived architecture work,
workstreams, ADRs, lane ownership, and frequent refactoring.

The biggest current weakness is not the philosophy. It is the runtime enforcement layer.

Today, `dev-skills` has stronger governance than Trellis, but weaker per-turn execution control.
Matt skills provide strong local engineering habits, but intentionally stop short of owning program
orchestration.

## What Each System Optimizes

### Trellis

Primary optimization:

- reliable task-centered execution across many AI platforms.

Core shape:

- `.trellis/workflow.md` as workflow source of truth,
- task directories as execution units,
- hooks and injected workflow breadcrumbs,
- per-turn guidance tied to task status,
- curated task context injected into implement/check agents.

Trellis is best understood as an AI execution harness.

### Matt Skills

Primary optimization:

- composable engineering thinking with minimal process ownership.

Core shape:

- small skills with narrow jobs,
- domain language via `CONTEXT.md`,
- ADR-aware design thinking,
- TDD, diagnosis, architecture review, issue shaping,
- no heavy runtime state machine.

Matt skills are best understood as an engineering skill library.

### Dev Skills

Primary optimization:

- large-program engineering governance for Rust-heavy repos.

Core shape:

- artifact authority chain:
  `product docs -> ADR -> workstream -> task ledger -> journal/handoff -> chat`
- explicit workstream lifecycle,
- architecture lanes and upper-planner mode,
- campaigns, bundles, validation gates, side-effect policy,
- review/verify/integrate separation,
- session recovery and worktree-aware execution.

Dev Skills is best understood as a project governance layer built on top of Codex-style skills.

## Where Dev Skills Is Stronger

### 1. Project truth stays in project artifacts

This is the most important design choice.

Trellis intentionally centralizes workflow behavior in `.trellis/workflow.md`. That is good for
execution consistency, but it can become a parallel control plane when a project already has ADRs,
architecture docs, and durable workstream ledgers.

`dev-skills` deliberately avoids:

- a second architecture truth that competes with ADRs,
- a second task truth that competes with `TODO.md`,
- journal-only decisions,
- workflow-only decisions that never land in project docs.

For large Rust systems, this is the correct bias.

### 2. Better support for architecture-scale work

Trellis is task-first.

`dev-skills` adds concepts that matter in large repos:

- architecture lanes,
- stable lane worktrees,
- upper-planner coordination,
- multi-bundle campaigns,
- shared-scope stops,
- integration order,
- side-effect policy.

These are not decorative abstractions. They map to real problems in large concurrent Rust work.

### 3. Better completion discipline

`dev-skills` explicitly separates:

- implementation,
- review,
- fresh verification,
- integration,
- closeout.

That is a stronger model than trusting “done” reports or stale terminal output.

### 4. Better alignment with fearless refactoring

Matt skills contribute the architectural language and refactoring posture.
`dev-skills` extends that into:

- workstream-backed refactors,
- evidence gates,
- architecture-lane sequencing,
- explicit ADR reconciliation.

This is a better fit for repeated deep refactors than a purely task-centered workflow.

## Where Trellis Is Stronger

### 1. Runtime enforcement

Trellis does a better job of reducing agent discretion during a live session.

Examples:

- workflow state is injected every turn,
- task status strongly drives the next recommended step,
- context loading is tied to task artifacts,
- implement/check roles are operationalized, not merely described.

`dev-skills` currently describes a stronger process than it enforces.

### 2. Context injection

Trellis is opinionated about the active task context:

- what to load,
- when to load it,
- which sub-agent receives it.

`dev-skills` has the right artifact model (`CONTEXT.jsonl`, workstreams, ADRs), but the runtime
bridge from artifact state to per-turn execution is still comparatively soft.

### 3. Frictionless entry

Trellis is optimized for:

- natural-language task intake,
- immediate routing,
- consistent behavior across many platforms.

`dev-skills` has more power, but it risks becoming too ceremonious unless routing stays sharp.

## Where Matt Skills Is Stronger

### 1. Skill sharpness

Matt skills are concise and easy to trust because each one has a narrow intent.

That keeps:

- mental overhead low,
- failure modes local,
- adaptation easy.

`dev-skills` is strongest when it preserves this property and only adds orchestration where repo
scale truly demands it.

### 2. Design pressure before implementation

Skills like:

- `grill-with-docs`,
- `improve-codebase-architecture`,
- `tdd`,
- `diagnose`

embody durable software engineering thinking without over-owning the full workflow.

`dev-skills` should continue to compose with these, not replace them.

## Current Risks In Dev Skills

### 1. Documented state machine, soft runtime

The repository already defines:

- orchestration phases,
- artifact contracts,
- gate taxonomy,
- planner state validation.

But many of these are still enforced socially through prompts instead of mechanically through
runtime breadcrumbs, intake scripts, or state guards.

Risk:

- the system looks rigorous on paper,
- but a long session still skips steps or accepts partial state.

### 2. Ceremony creep

Large-project discipline is good.
Applying it too often is not.

If medium work routinely expands into:

- audit,
- grill,
- product shaping,
- lane planning,
- workstream open,
- task split,
- review,
- verify,

then users will route around the workflow.

### 3. Inconsistent artifact-to-execution bridge

The repo has strong artifacts.
What it still needs is a more mechanical answer to:

- what the active unit of work is,
- which docs must be read now,
- which stop conditions are currently armed,
- what “fresh enough” evidence means for this slice.

### 4. Overfitting to one operator style

This is acceptable if the target audience is “large Rust repos operated by people who already want
ADR/workstream/lane governance”.

It is a problem only if the repo aims to become a general-purpose workflow layer.

## Working Hypothesis

The correct direction is:

- keep `dev-skills` artifact authority as-is,
- keep composing with Matt skills,
- borrow Trellis runtime hardening selectively,
- do not borrow Trellis source-of-truth centralization.

In short:

- Trellis-like runtime control,
- Matt-skill composability,
- project-owned ADR/workstream truth,
- Rust-program governance.

## Refactor Themes To Validate

1. Add a lightweight runtime breadcrumb model for `dev-skills`:
   - current phase,
   - active workstream/task/bundle,
   - required next step,
   - validation freshness,
   - stop conditions.

2. Strengthen artifact validation:
   - completed task without fresh verification should fail,
   - active workstream with drift between `TODO.md`, `TASKS.jsonl`, and `CAMPAIGNS.jsonl` should
     fail,
   - handoff-only decisions should be surfaced as authority drift.

3. Prove workflow scale choices on real repos:
   - small work should stay small,
   - medium work should open exactly one durable lane when needed,
   - large repos should justify planner/lane split with evidence.

4. Add evaluation scenarios that measure usefulness, not only compliance:
   - fewer clarification turns,
   - faster session recovery,
   - fewer missed docs,
   - fewer false completion claims,
   - lower cross-lane collision risk.

## Real-Repo Readiness

`repo-ref/nako` and `repo-ref/hajimi` are suitable validation targets because both already contain:

- `AGENTS.md`,
- `CONTEXT.md`,
- ADR sets,
- durable workstreams,
- targeted validation commands,
- large Rust workspace structure.

They can be used to test whether `dev-skills`:

- chooses the right workflow scale,
- avoids redundant bootstrapping,
- reads the right authority docs,
- proposes useful lane/workstream routing,
- and keeps evidence discipline without becoming heavy for no benefit.

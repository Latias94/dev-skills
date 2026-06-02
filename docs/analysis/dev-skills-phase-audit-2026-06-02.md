# Dev Skills Phase Audit — 2026-06-02

## Purpose

This audit closes the current refactor and experiment phase.

It does not claim the full long-term objective is finished forever.
It does claim that the current repository now contains enough evidence to answer a narrower but
important question:

> Is `dev-skills` directionally wrong, or does it now have a defensible architecture and runtime
> hardening path compared with Trellis and Matt skills?

## Scope Of Evidence

This audit is grounded in current repository artifacts, scripts, tests, and real-repo runs using:

- `repo-ref/nako`
- `repo-ref/hajimi`
- `repo-ref/skills`

Key evidence families:

- comparison and decision docs
- readiness/audit scripts
- runtime hardening scripts
- scenario evaluation scripts
- real-repo rehearsal notes
- unit tests covering those artifacts

## What Is Now Proven

### 1. The core direction is not fundamentally wrong

Current evidence supports keeping:

- project-owned truth in ADRs, architecture docs, workstreams, tasks, campaigns, and evidence
- Matt-style lower-level engineering skills
- lane/workstream/program abstractions for large Rust repos

Why this is now provable:

- the repo contains direct three-way comparison docs
- `nako` and `hajimi` were used repeatedly as distinct benchmarks
- no real-repo run produced evidence that project-owned truth must be replaced by a Trellis-style
  workflow file

### 2. `READINESS` vs `AUDIT` is a real and necessary distinction

This is no longer only a design opinion.

Why this is now provable:

- `repo-ref/nako` repeatedly yields a ready active queue
- `repo-ref/hajimi` repeatedly yields a historical-audit posture
- scripts, docs, and tests now align around:
  - `Operating Mode`
  - `Implementation Horizon`
- adversarial scenarios proved both over-cautious and over-aggressive behavior can be detected

### 3. Runtime hardening now exists as a layered bridge

It is no longer accurate to say the repo only has governance docs.

Derived runtime layers now exist through:

1. `planner_breadcrumb.py`
2. `planner_payload.py`
3. `dispatch_rehearsal.py`
4. `handoff_chain_rehearsal.py`
5. `planner_turn_prelude.py`
6. `planner_prompt_wrapper.py`

Why this is now provable:

- these scripts exist
- they are covered by unit tests
- they were exercised on real repos
- they are documented in user-facing and evaluation-facing docs

### 4. Runtime state is now consumed, not merely generated

This is a critical threshold that earlier iterations had not crossed.

Why this is now provable:

- payloads carry `runtime_prompt_block`
- dispatch rehearsals carry `runtime_prompt_block`
- handoff-chain prompts share the same derived control state
- planner turn prelude and prompt wrapper move the same state to the prompt boundary

### 5. The system can now reject both major planner boundary errors

Those errors are:

- fabricated execution when no active queue exists
- unnecessary planner-only hesitation when a bounded active unit is ready

Why this is now provable:

- `hajimi` adversarial execution scenario fails correctly
- `nako` adversarial planner-only scenario fails correctly
- medium-task downshift behavior improved after scenario pressure

## What Is Not Yet Proven

### 1. Automatic per-turn injection parity with Trellis

The repository now has a derived-only rehearsal for prompt-boundary injection, but it does not have
platform-level automatic hook wiring.

What exists:

- `planner_turn_prelude.py`
- `planner_prompt_wrapper.py`

What is still unproven:

- that the same behavior survives real automatic per-turn injection across platforms
- that wrapper usage is enough in practice without native integration

### 2. Live multi-role execution reliability under real model behavior

Read-only rehearsals and prompt artifacts are much stronger now, but this is still weaker evidence
than repeated live planner/worker/reviewer/verifier/integrator runs.

What is still unproven:

- whether real role agents consistently obey the derived prompts
- whether result markers remain reliable under actual long-running execution
- whether integration can stay evidence-first in messier real sessions

### 3. Whether historical evidence normalization should become a product goal

`nako` and `hajimi` still expose substantial historical drift.

What is still unproven:

- whether `dev-skills` should actively push normalization campaigns
- or treat this drift as optional hygiene rather than default productized workflow pressure

## Directional Errors That Can Now Be Rejected

The following concerns are no longer supported by current evidence:

### Rejected concern 1: "Dev-skills should probably become Trellis with bigger docs"

Rejected because:

- the repo now has a working derived runtime bridge
- project-owned truth remains intact
- no evidence showed that Trellis task truth must replace workstream/ADR authority

### Rejected concern 2: "The runtime story is still only prompt prose"

Rejected because:

- scripts, payloads, rehearsals, preludes, wrappers, and tests now form a concrete runtime bridge

### Rejected concern 3: "READINESS/AUDIT is too abstract to help"

Rejected because:

- `nako` and `hajimi` repeatedly demonstrate different but correct planner behaviors under that split

## Remaining Risks

### Risk 1: Runtime consumption still depends on explicit usage

The bridge is now real, but it still depends on:

- wrapper usage
- prelude usage
- or script consumption

This is a narrower risk than before, but still the main remaining runtime gap.

### Risk 2: Ceremony creep can still return

The medium-task path improved, but this pressure can regress.

Any future change that causes bounded work on medium repos to re-escalate into planner-heavy flows
should be treated as a regression.

### Risk 3: Historical drift may still dominate operator attention

The split between readiness and audit helps, but operator cost can still degrade if historical audit
noise becomes the main visible output too often.

## Net Judgment

The current repository now supports a stronger conclusion than before:

- `dev-skills` is not directionally broken
- the repo is no longer only a governance layer with vague runtime aspirations
- the remaining gap to Trellis is now mostly automation and platform integration, not architectural
  confusion

The best short description of current status is:

> artifact-first governance with an increasingly credible derived runtime bridge

## Recommended Next Phase

Do not reopen the foundational architecture debate unless new real-repo evidence contradicts the
current findings.

Preferred next-phase work:

1. live prompt-boundary experiments using `planner_prompt_wrapper.py`
2. selective hook-style rehearsal or platform integration experiments
3. repeated live role-chain validation on `nako`
4. policy decision on whether historical evidence normalization is a core workflow goal

## Bottom Line

This phase succeeded.

Not because every future problem is solved.
Because the repo now has evidence-backed answers to the central questions that originally justified
the refactor:

- keep project-owned truth
- keep Matt-skill composability
- borrow Trellis runtime discipline selectively
- validate on real repos
- and move runtime hardening from theory into consumable artifacts

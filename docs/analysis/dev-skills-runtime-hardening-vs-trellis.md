# Dev Skills Runtime Hardening vs Trellis

## Core Judgment

The main direction is still correct:

- keep project truth in ADRs, architecture docs, workstreams, tasks, campaigns, and evidence
- keep Matt skills as the lower-level engineering toolkit
- harden runtime behavior by deriving compact control hints from those artifacts

The main gap is also unchanged:

- `dev-skills` has a strong governance model
- Trellis has a stronger live execution model

The wrong refactor would be copying Trellis task centralization.
The right refactor is borrowing Trellis runtime sharpness without surrendering project-owned truth.

## What Trellis Gets Right

Trellis is not merely "well documented".
It operationalizes several things that `dev-skills` still does only partially:

1. per-turn workflow-state injection
2. explicit active-unit-of-work resolution
3. subagent-specific context injection
4. phase transitions with runtime consequences
5. tests that guard the workflow contract itself

This is why Trellis feels harder to drift away from during long sessions.

## What Dev Skills Must Not Copy

Trellis assumes task directories are the dominant control surface.
That is a good fit for task-centric execution, but it is a weak fit for:

- ADR-heavy architecture evolution
- multi-workstream lane ownership
- program-level planning across related worktrees
- historical audit vs active readiness separation
- repeated fearless refactoring across capability seams

If `dev-skills` copied Trellis by making a workflow file or task folder the new top-level truth, it
would create a competing governance layer and weaken the exact thing that currently makes the system
worth having.

## The Correct Synthesis

### Keep from Matt skills

- narrow skills with crisp intent
- deepening-oriented architecture language
- strong local engineering habits
- domain vocabulary through `CONTEXT.md`

### Keep from current dev-skills

- authority order rooted in repo artifacts
- workstream/task/campaign split
- readiness vs audit split
- review/verify/integrate separation
- lane/program planning for large Rust repos

### Borrow from Trellis

- runtime injection discipline
- explicit active state resolution
- prompt-shape consistency
- workflow-contract testing

## Derived Runtime Bridge

The current best move is a derived runtime bridge.

That means:

- no committed workflow state file becomes authoritative
- no planner breadcrumb is edited manually
- no prompt relies on memory alone when the active queue is derivable

Instead:

1. read repo artifacts
2. derive the compact runtime snapshot
3. inject that snapshot into planner-style turns
4. continue to treat the repo artifacts as truth

This is now partially implemented through:

- `skills/engineering/plan-engineering-program/scripts/planner_breadcrumb.py --format prompt`
- `skills/engineering/plan-engineering-program/scripts/planner_turn_prelude.py`

That output is the seed of a Trellis-like runtime layer without importing Trellis' truth model.

## Directional Errors To Avoid

### Error 1: Over-planning medium work

If medium tasks routinely require planner/lane/campaign overhead, the workflow will be routed around.

Validation signal:

- repeated real-repo scenarios where the chosen route is heavier than a direct bounded workstream or
  direct `tdd`/`diagnose` path

### Error 2: Letting runtime stay optional

If runtime hints are available only when someone remembers to run a script manually, the system will
continue to drift under long sessions.

Validation signal:

- planner and integrator outputs remain inconsistent even when artifact state is stable

### Error 3: Creating a second source of truth

If runtime hardening becomes a committed control file that humans must keep in sync, the system will
gain one more drift vector instead of removing one.

Validation signal:

- users have to repair the runtime layer separately from ADR/workstream/task state

### Error 4: Treating historical drift as an execution blocker

This was already disproven by `nako` and `hajimi`.

Validation signal:

- ready active queues get blocked by unrelated historical evidence gaps

## How To Prove The Skills Solve Real Problems

A skill system solves real problems only if it reliably improves decisions and execution under messy
repo conditions.

Proof should be collected along four axes:

1. route choice:
   - does it choose the right workflow scale?
2. runtime discipline:
   - does it keep the active unit of work and next step obvious?
3. artifact integrity:
   - does it detect and localize drift instead of hand-waving it?
4. operator cost:
   - does the workflow stay worth using repeatedly?

## Concrete Validation Loop

### 1. Readiness benchmark

Use `repo-ref/nako`.

Check whether the system can:

- identify the active queue
- derive the next bounded unit
- name the required context
- avoid reopening planning unnecessarily

### 2. Historical audit benchmark

Use `repo-ref/hajimi`.

Check whether the system can:

- explain zero assignable horizon clearly
- surface historical drift without sounding blocked or confused
- avoid pretending that audit findings are active-queue blockers

### 3. Adversarial medium-task benchmark

Use a medium-sized real task where planner escalation is tempting but unnecessary.

Check whether the system:

- stays on a direct path
- avoids fabricating campaign/lane complexity
- still preserves evidence and verification discipline

### 4. Runtime consumption benchmark

Force planner-style prompts to consume the derived runtime block and compare against runs that do
not use it.

Measure:

- fewer missed context docs
- fewer wrong next-step recommendations
- fewer false blocked states
- lower repetition after session resume

## Bottom Line

The system is not directionally broken.

Its main unresolved problem is that runtime enforcement still trails its governance ambition.
That is a fixable implementation gap, not a reason to abandon the architecture.

The right end state is:

- Matt-skill sharpness for local engineering work
- dev-skills governance for large Rust programs
- Trellis-grade runtime discipline derived from repo artifacts

Not:

- Trellis truth model copied wholesale
- or a looser prompt-only governance layer that never really bites at runtime

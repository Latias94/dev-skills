# Dev Skills Real-Repo Evaluation Framework

## Goal

This framework evaluates whether `dev-skills` actually improves engineering outcomes on real
repositories instead of only sounding rigorous in skill prompts.

It is designed for repeated runs on repositories under `repo-ref/`, especially large Rust
workspaces such as:

- `repo-ref/nako`
- `repo-ref/hajimi`

## What We Are Testing

We are not only testing “did the skill follow the script?”

We are testing four layers:

1. routing correctness,
2. artifact correctness,
3. execution usefulness,
4. operator cost.

## Layer 1: Routing Correctness

Question:

- did the system pick the right workflow scale?

Checks:

- small bounded task routes to direct `tdd` or `diagnose`,
- medium durable change routes to one workstream, not many,
- large repo parallelization routes to planner/lane shape only when justified,
- stale substrate routes to repair before assignment,
- product ambiguity routes to shaping or grilling before implementation.

Failure examples:

- creating a workstream for a typo,
- asking for multi-lane planning when one bounded task is enough,
- assigning implementation while authority docs are obviously stale.

## Layer 2: Artifact Correctness

Question:

- do durable artifacts agree with each other?

Checks:

- `WORKSTREAM.json` agrees with `TODO.md`, `MILESTONES.md`, and gates,
- `TASKS.jsonl` agrees with `TODO.md`,
- `CAMPAIGNS.jsonl` agrees with current lane/campaign claims,
- `HANDOFF.md` does not become the only place a durable decision exists,
- closeout promotes durable knowledge into ADRs, architecture docs, or workstream docs.

Failure examples:

- task marked complete but no fresh evidence exists,
- campaign claims active autonomy without stop conditions,
- handoff records an architecture decision that never lands in ADR/docs.

## Layer 3: Execution Usefulness

Question:

- does the workflow help the agent make better decisions and finish work more reliably?

Checks:

- fewer missed prerequisite docs,
- fewer false “done” claims,
- better validation targeting,
- clearer next-step recommendations after each phase,
- better recovery from resumed sessions,
- better decomposition of large refactors into independent slices.

Failure examples:

- skill still asks “what next?” when repo evidence already answers it,
- worker gets a task with unclear scope or validation,
- verification repeats stale commands or irrelevant wide checks.

## Layer 4: Operator Cost

Question:

- is the system worth using repeatedly?

Checks:

- total clarification turns,
- time to first useful recommendation,
- amount of redundant reading,
- number of artifact updates required before safe execution,
- whether users would realistically keep using the workflow.

Failure examples:

- a medium task requires excessive ceremony,
- same context must be restated across sessions,
- lane/program abstractions are introduced without practical leverage.

## Scorecard

Use a 0-2 score per category.

### Routing

- `0`: wrong scale or unsafe assignment
- `1`: mostly right but noisy or over/under-scoped
- `2`: right scale with clear reasoning

### Artifact Integrity

- `0`: contradictory or missing authoritative state
- `1`: minor drift or ambiguous ownership
- `2`: artifacts agree and support action

### Execution Quality

- `0`: workflow does not meaningfully improve execution
- `1`: some help, but gaps remain
- `2`: clearly improves safe progress

### Operator Cost

- `0`: too heavy to sustain
- `1`: acceptable with friction
- `2`: efficient for the repo scale

## Scenario Template

For each evaluation scenario, record:

```md
## Scenario: <name>

Repo: <path>
Scale expectation: direct | workstream | lane | program
Prompt:
<the user-style request>

Expected route:
- first skill
- supporting skill(s)
- artifact reads required
- side effects that must not happen yet

Success signals:
- ...

Failure signals:
- ...

Score:
- Routing:
- Artifact Integrity:
- Execution Quality:
- Operator Cost:

Notes:
- ...
```

## Initial Scenario Set

### NAKO-001: Existing large repo, next task unclear

Repo:

- `repo-ref/nako`

Prompt:

- “Use dev-skills to inspect this repo, identify active lanes or workstreams, and recommend the
  next safe task.”

Expected route:

- `audit-project-scale` or `plan-engineering-program`
- read `AGENTS.md`, `CONTEXT.md`, `docs/architecture/LANES.md`, active workstreams
- no code changes

### NAKO-002: Workstream continuation

Prompt:

- “Resume the active workstream and choose the next bounded task.”

Expected route:

- `resume-workstream`
- then `run-workstream-task` only if evidence is sufficient

### HAJIMI-001: Architecture-lane suitability

Repo:

- `repo-ref/hajimi`

Prompt:

- “Decide whether this repo should be worked as direct task, workstream, or architecture lane for
  the current active queues.”

Expected route:

- `audit-project-scale`
- likely escalate to planner-aware path because multiple active workstreams already exist

### HAJIMI-002: Refactor campaign readiness

Prompt:

- “Inspect the current workstreams and tell me whether any same-lane campaign is actually ready for
  autonomous execution.”

Expected route:

- `plan-engineering-program`
- must check active workstreams, gates, validation, and stop conditions

## Required Evidence For Each Run

Every run should capture:

- which files were read,
- which workflow scale was chosen,
- which phase the agent claimed it was in,
- what it considered authoritative,
- whether any state drift was found,
- what the next action was,
- whether the action was blocked and why,
- the derived planner breadcrumb, if available.

## What Success Looks Like

`dev-skills` is working if repeated runs on `nako` and `hajimi` show:

- correct workflow-scale choice,
- low ambiguity about next steps,
- strong respect for repo-owned authority docs,
- useful bounded decomposition,
- fresh evidence requirements before completion,
- and acceptable operator cost for large Rust work.

## What Would Trigger A Larger Refactor

Any of the following should trigger structural change to the skill system:

- repeated confusion about the active phase,
- repeated drift between artifact truth and runtime behavior,
- planner skills that cannot tell whether work is actually assignable,
- repeated overuse of ceremony on medium tasks,
- or repeated need for the operator to restate the same authority hierarchy.

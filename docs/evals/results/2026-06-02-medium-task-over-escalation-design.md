# Medium Task Over-Escalation Design

## Why This Exists

The current real-repo evaluator is now good at two boundary failures:

- fabricated execution on a historical-only repo
- unnecessary planner caution when a ready task exists

Those both live on the planner/worker boundary.

The next likely directional error is different:

- a medium task that should stay at direct-task or single-workstream scale gets expanded into
  planner-heavy ceremony

This note defines that failure mode before adding a dedicated fixture or scenario.

## Failure We Want To Catch

The bad behavior is not:

- choosing a planner on a truly large ambiguous repo
- or refusing execution when readiness is genuinely missing

The bad behavior is:

- introducing planner/lane/program structure when one bounded workstream or even a direct
  `tdd`/`diagnose` route would have been enough

That is the concrete form of the “ceremony creep” risk recorded in
`docs/analysis/dev-skills-vs-trellis-vs-matt-skills.md`.

## Expected Good Behavior

For a medium task, the workflow should usually do one of:

1. direct route:
   - `tdd`
   - `diagnose`
2. single durable lane-local route:
   - `resume-workstream`
   - `run-workstream-task`
   - one new workstream if durable artifacts are actually required

It should usually avoid:

- `plan-engineering-program`
- lane fan-out
- campaign orchestration
- multi-terminal framing

unless repo evidence clearly shows:

- shared-scope collision risk,
- multiple active queues needing arbitration,
- substrate repair blocking execution,
- or product/ADR uncertainty that really must be resolved first.

## Proposed Scenario Shape

This scenario should not be forced onto `repo-ref/nako` or `repo-ref/hajimi` directly.

Why:

- both repos are large enough that planner-aware behavior can be rational even when a user asks for
  a small slice
- that would muddy the signal about whether the workflow is over-escalating *because of the task* or
  simply because of repo scale

The cleaner design is:

- a dedicated medium-task fixture repo under `repo-ref/`
- or a documented synthetic scenario against an existing repo subsection with a very narrow prompt

## Minimum Fixture Requirements

If a new fixture is added later, it should have:

- `AGENTS.md`
- `CONTEXT.md`
- a small but non-trivial codebase
- at most one active workstream
- no architecture-lane substrate
- one bug/feature prompt that is clearly bounded

The success condition is that `dev-skills` does **not** escalate to:

- upper planner,
- lane campaigns,
- or multi-terminal orchestration.

## Scoring Hook To Add Later

When this scenario is implemented, add one new evaluator dimension or expectation:

- `should_avoid_program_escalation_for_medium_task`

It should fail when:

- `expected_scale` is `direct` or `workstream`
- but the recommended route is `plan-engineering-program`
- without explicit repo evidence of shared-scope, substrate, or ADR blockers

## Comparison Meaning

This future scenario should sharpen the three-way comparison:

- `Trellis-like` should score well if the route stays task-centered and context is tight
- `Matt-skills-like` should score well if the route stays sharp and design-aware
- `dev-skills` should only score well if it proves restraint instead of reflexive orchestration

## Recommendation

Do not fake this scenario with `nako` or `hajimi`.

Use the current note as a design contract, then later add either:

1. a dedicated fixture repo under `repo-ref/`, or
2. a small real repo already present under `repo-ref/` if one actually matches the medium-task
   shape.

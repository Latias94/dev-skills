# Campaign Planning

A campaign is the unit that keeps a lane terminal productive without making the goal unbounded.

## Lane Goal Bundle

A lane goal bundle is the approved execution unit for a long-running terminal. It is larger than a
tiny task and smaller than a whole architecture area.

Good bundle:

- one lane and one stable worktree,
- one active workstream or a short same-lane queue,
- one to three ready task IDs,
- disjoint owned scopes and explicit shared scopes,
- one validation path the lane terminal can run,
- context manifest path,
- clear stop conditions.

If bundles routinely finish too quickly, combine adjacent ready same-lane tasks into a larger bundle
only when they share a lane, have clear dependencies, avoid shared-scope ambiguity, and use one
validation path.

When the ready queue is thin, do not ask the user for more tasks first. Run read-only code/docs
reconnaissance with `zoom-out`, `plan-architecture-lane`, or scoped `improve-codebase-architecture`,
then propose implement-now, plan-first, ADR-first, wait-for-active-branch, or defer candidates.

## Good Campaign

- one lane and one stable worktree,
- ordered bundles or workstreams,
- 45-120 minutes of coherent autonomous work when feasible,
- clear owned scopes and shared scopes,
- per-step validation and evidence updates,
- explicit auto-advance rule,
- approved side-effect policy for commit/sync/merge when desired,
- stop conditions for failed gates, ADR/schema/contract changes, shared scopes, related repo
  decisions, dirty unrelated files, and unapproved side effects.

## Side-Effect Policy

A campaign may pre-approve routine side effects so long goals do not stop after every slice:

- auto-commit at accepted task/bundle boundaries after review, fresh gates, evidence updates, and
  clean scope check;
- auto-sync main into the lane worktree after accepted commits when conflicts are absent;
- auto-merge lane back to main after review, verification, and post-merge gate when the campaign
  explicitly allows it.

Never auto-continue through merge conflicts, failed gates, unrelated dirty files, public contract or
ADR/schema changes, related-repo release/version decisions, or push operations unless the user
explicitly pre-approved that exact side effect.

## Parallelism Rule

Use parallel lane campaigns only when file scopes and contracts are disjoint. If tasks depend on each
other or touch hot shared files, call it out and create a serial lane campaign instead.

## Goal Text

Codex goals should reference the approved campaign, not replace it:

```text
Set the current Codex goal to execute approved lane campaign <LANE>-<DATE>-01.
Auto-advance through the listed steps only when each gate passes and evidence is updated. Stop on
shared scopes, ADR/schema/contract changes, failed gates, missing context, dirty unrelated files, or
unapproved side effects.
```

## Lane Next-Goal Proposal

When a lane finishes a campaign, it should propose the next same-lane medium goal:

- why this is the next best lane move,
- which docs/code evidence supports it,
- owned/shared scopes,
- needed workstream or ADR updates,
- validation gates,
- whether it is implement-now, plan-first, ADR-first, wait-for-active-branch, or defer.

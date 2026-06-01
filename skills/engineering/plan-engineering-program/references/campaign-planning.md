# Campaign Planning

A campaign is the unit that keeps a lane terminal productive without making the goal unbounded.
Record draft and approved campaigns in workstream `CAMPAIGNS.jsonl`; local planner state records
which terminal or worktree is running them.

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

Choose a bundle instead of a single task when the task is mostly mechanical, validation is shared
with its neighbors, and the same lane terminal would otherwise stop within a few minutes. Choose a
campaign instead of a bundle when several ready bundles share one lane, have an explicit order, and
can auto-advance through gates without changing ADRs, public contracts, or shared scopes.

If bundles routinely finish too quickly, combine adjacent ready same-lane tasks into a larger bundle
only when they share a lane, have clear dependencies, avoid shared-scope ambiguity, and use one
validation path.

When the ready queue is thin, do not ask the user for more tasks first. Run read-only code/docs
reconnaissance with `zoom-out`, `plan-architecture-lane`, or scoped `improve-codebase-architecture`,
then propose implement-now, plan-first, ADR-first, wait-for-active-branch, or defer candidates.

## Good Campaign

- one lane and one stable worktree,
- ordered bundles or workstreams,
- an `Autonomy Horizon`: expected autonomous duration, number of bundles, checkpoint cadence, and
  stop rules,
- 45-120 minutes of coherent autonomous work when feasible; longer only when gates and side-effect
  policy are explicit,
- clear owned scopes and shared scopes,
- per-step validation and evidence updates,
- explicit auto-advance rule,
- standard side-effect policy for commit/sync/merge, with explicit deny rules,
- stop conditions for failed gates, ADR/schema/contract changes, shared scopes, related repo
  decisions, dirty unrelated files, and unapproved side effects.

## Side-Effect Policy

A campaign may pre-approve routine side effects so long goals do not stop after every slice:

- auto-commit at accepted task/bundle boundaries after review, fresh gates, evidence updates, and
  clean scope check;
- auto-sync main into the lane worktree after accepted commits when conflicts are absent;
- auto-merge lane back to main after review, verification, and post-merge gate when the campaign
  explicitly allows it.

Every campaign plan should state one of these policies:

- `manual`: planner must ask before commit, merge, sync, worktree creation, or related-repo changes.
- `auto-commit-sync`: commit accepted slices and sync main into the lane worktree after clean gates.
- `auto-commit-sync-merge`: also merge accepted lane slices back to main when the listed integration
  gates pass and the target branch policy allows it.

Never auto-continue through merge conflicts, failed gates, unrelated dirty files, public contract or
ADR/schema changes, related-repo release/version decisions, or push operations unless the user
explicitly pre-approved that exact side effect.

## Parallelism Rule

Use parallel lane campaigns only when file scopes and contracts are disjoint. If tasks depend on each
other or touch hot shared files, call it out and create a serial lane campaign instead.

## Terminal Budget Rule

For a large repo, the upper planner should usually identify three to five large candidate directions,
then activate at most three lane/worker terminals by default. More terminals are justified only
when scopes, gates, branches, and shared contracts are clearly disjoint.

If the repo first needs architecture substrate repair, lane-map creation, or module-boundary
deepening, prefer one planner/recon terminal or one serial lane campaign. Do not split uncertain
architecture cleanup across several implementation terminals.

## Campaign Depth Rule

Do not hand a lane terminal a five-minute goal when the repo evidence supports a larger bounded
campaign. Prefer this order:

1. approved lane campaign with auto-advance gates,
2. lane goal bundle with one to three related tasks,
3. one bounded task,
4. read-only reconnaissance when no implementation slice is ready.

If a campaign cannot reach a useful autonomy horizon, explain which missing document, gate, ADR,
or code boundary prevents it. Do not hide the problem behind a tiny task.

When implementation is not ready, report:

```text
Implementation Horizon: 0
Recon Horizon: 30-60 min read-only
Blockers: <missing LANES.md | no active queue | closed history only | unclear gates>
Next gate to unlock assignment: <mechanical substrate repair or planning artifact>
```

Closed, complete, or completed workstreams can seed candidate discovery, but they are not approved
execution queues. Treat `continue_policy`, handoff follow-ons, and old `current_task` values as
evidence to cross-check against current code, ADRs, and lane maps.

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

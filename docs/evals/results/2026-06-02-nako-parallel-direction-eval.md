# Nako Parallel Direction Eval — 2026-06-02

## Goal

Validate whether the workflow can identify suitable parallel directions instead of blindly spawning
more workers.

This eval uses `repo-ref/nako` because it has:

- a lane registry,
- one active ready queue,
- multiple idle/follow-on lane candidates,
- enough real workstream history to test planner restraint.

## Current Dispatch Fact

`dispatch_rehearsal.py` reports:

- `parallel_safe_now: false`
- reason:
  `only one ready active unit is derived from current artifacts`

Current ready active unit:

- lane:
  `library-metadata-control-plane`
- workstream:
  `generated-artifact-bulk-metadata-apply`
- task:
  `GABMA-020`
- campaign:
  `GABMA-20260601-01`

## Immediate Parallelism Decision

Result: do not parallelize implementation now.

Reason:

- only one active ready implementation unit exists
- `LANES.md` explicitly says several follow-ons must wait until this active queue is reviewed or
  split
- spawning implementation workers for idle/follow-on lanes would turn candidates into fake active
  queues

Correct current execution shape:

- one worker chain for `GABMA-020`
- reviewer/verifier/integrator stay on the same active unit
- upper planner may run read-only reconnaissance in parallel

## Next-Wave Parallel Candidates

These are not ready implementation queues yet.
They are suitable for parallel reconnaissance or new workstream planning.

### `storage-vfs`

Candidate themes:

- cache repair
- source fingerprint escalation
- PostgreSQL runtime harness
- scan scheduling

Why it can become parallel:

- owned scopes are distinct around VFS/storage diagnostics
- lane exists in `LANES.md`

Why it is not implementation-ready now:

- new workstream required
- shared boundaries with scan/probe and playback staging need planner coordination

### `playback-transcode`

Candidate themes:

- resource admission queueing
- remote workers
- LL-HLS/CMAF
- HEVC/AV1 policy
- subtitle burn-in
- hardware smoke evidence

Why it can become parallel:

- owned playback/transcode scopes are separate from current metadata control-plane task

Why it is not implementation-ready now:

- candidates need splitting into separate workstreams
- playback artifact I/O pressure is explicitly deferred/follow-on

### `web-product`

Candidate themes:

- backend/API contract follow-on
- generated SDK coordination
- broader player UX
- desktop/native playback decisions

Why it can become parallel:

- lane has distinct frontend/product ownership

Why it is not implementation-ready now:

- API/contract impact from `GABMA-020` must be known before Web/API work starts

### `addons-automation`

Candidate themes:

- official addon alpha smoke
- addon lifecycle
- outbound task dispatch
- automation jobs

Why it can become parallel:

- lane ownership is separate and can use related-repo coordination rules

Why it is not implementation-ready now:

- may depend on generated artifact apply outcomes
- new workstream and cross-repo sync policy are required

## Must Wait For `GABMA-020` Review Or Split

Do not start implementation for:

- provider mapping breadth
- Admin settings restoration
- playback artifact I/O enforcement
- actual release publication
- one-command release-gate wrapping
- official addon alpha smoke
- generated client contract changes
- schema migrations
- Admin apply workflow route state

These may be future candidates, but they are not ready active queues.

## Recommended Terminal Layout

Current phase:

- Terminal 1:
  upper planner / integrator, read-only status and result intake
- Terminal 2:
  `GABMA-020` worker on one bounded branch/worktree
- Terminal 3:
  reviewer/verifier for the same worker result
- Terminal 4+:
  future-lane reconnaissance only for `storage-vfs`, `playback-transcode`, `web-product`, or
  `addons-automation`

After `GABMA-020` is reviewed, verified, and integrated or split:

- create one approved workstream/campaign per lane candidate
- bind each to a separate worktree only after owned/shared scopes and validation gates are explicit

Potential future worktree names:

- `nako-ws-storage-vfs-followon`
- `nako-ws-playback-transcode-followon`
- `nako-ws-web-product-followon`
- `nako-ws-addons-automation-followon`

## Evaluation

Result: `PASS`

Why it passes:

- correctly rejects immediate parallel implementation
- identifies future parallel lane candidates
- separates parallel reconnaissance from parallel execution
- does not fabricate active queues from idle/follow-on lanes
- names which directions must wait for `GABMA-020` review or split

## Meaning For The Workflow

This supports the original workflow intent:

- do not maximize agent count blindly
- keep implementation serialized when only one active unit is ready
- let the upper planner run parallel reconnaissance for future lanes
- promote candidates into parallel implementation only after workstreams, scopes, gates, and
  ownership are explicit

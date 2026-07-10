# Concurrent Writes

## Invariant

**Immutable shards, derived rollups.** Normal writers create new facts. The integration owner renders
shared views only after Git state is integrated.

This is a merge protocol, not a lock. Memory records continuity and evidence; it does not reserve
files, coordinate task ownership in real time, or replace an issue tracker.

## Writer Contract

- Every normal fact gets a generated `record_id`, a UUID-backed filename, and an exclusive local create.
  The filename makes independent clones choose distinct paths even when their clocks and titles match.
- `timestamp` is a display and scan hint, not a globally authoritative order. Use `supersedes` to state
  causality between snapshots.
- Set `producer_id` to the machine or agent that created the shard and `run_id` to the local session when
  either helps discovery. These fields are evidence, not locks.
- Give each parallel lane a stable `registration_id`. Registration updates are successor snapshots with
  `supersedes: <prior record_id>`; repeat `--supersedes` when one integration snapshot resolves several heads.
- A successor may supersede only `Work Registration` snapshots from the same `registration_id`. Local writes
  reject visible violations; integration refuses to render incomplete or cross-lane lineage.
- `--path` is a controlled exception for a human-selected immutable path. It cannot target `index.md`,
  `log.md`, or `current-state.md` and refuses to overwrite an existing file.

## Integration Contract

- Merge immutable shards first. If two successor snapshots claim the same predecessor, preserve both as
  evidence and create an explicit resolved successor during integration.
- Run `render --check` after pulling or rebasing. It compares the shared views to a deterministic render
  of immutable shards.
- One integration owner runs `render --owner <id>` and commits any changed rollups. Root `index.md` stays
  stable navigation; `current-state.md` and `log.md` are materialized views.
- If a rollup conflicts, preserve the shards, resolve or regenerate the rollup, and validate. Never discard
  a shard merely because a view is stale.

## External Runtimes

Existing `docs/workstreams/**/WORKSTREAM.json`, `TODO`, `HANDOFF`, and JSONL task files are mutable workflow
runtimes outside this bundle. Engineering memory must not claim ownership of them or mirror their live state.
Create a registration shard with `--external-runtime <repo-relative-manifest-path>` and cite task IDs or commits
as needed. `validate` reports an active manifest only when no open registration links to it; it does not impose
one schema on external runtimes. The association belongs to the registration lineage, so successors inherit it.
Unlinked manifests older than 30 days are advisory drift signals.

## Migration

Existing bundles remain readable. Keep legacy `current-state.md`, `log.md`, fixed-name registrations, and
progress ledgers as historical evidence. A root rollup without the derived marker is **not** safe for normal
rendering: `render --check` reports it as unadopted and `render --owner` refuses to replace it. After review,
an integration owner runs `render --owner <id> --adopt-rollups`; the command creates immutable `legacy/`
snapshots with the original path and SHA-256 before materializing derived views. Start new facts as immutable
shards and create a new registration lineage for active work. `validate` reports legacy records that lack
`record_id` and gives a non-destructive next action.

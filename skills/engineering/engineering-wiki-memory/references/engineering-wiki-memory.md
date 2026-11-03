# Engineering Wiki Memory Reference

This skill is a continuity sidecar built on the Open Knowledge Format (OKF). It is intentionally
smaller than a general OKF authoring toolkit: it preserves decisions, handoffs, lane identity, and
verification evidence that would otherwise be lost between agent runs.

## OKF boundary

The OKF v0.2 hard rule is deliberately small:

1. Every non-reserved Markdown file has a parseable YAML frontmatter block.
2. Every such block has a non-empty `type` field.

`index.md` and `log.md` are reserved navigation and history files. Unknown types, extra frontmatter
keys, missing optional fields, missing indexes, and broken links remain consumable. A root `index.md`
may declare `okf_version: "0.2"`; the memory script does this for new bundles.

The standard v0.2 fields are `type`, `title`, `description`, `resource`, and `tags`, with optional
provenance, trust, lifecycle, and attestation families. `generated`, `verified`, `status`,
`stale_after`, and `sources` are the important optional signals for a curated knowledge bundle.
The script also emits engineering extensions such as `record_id`, `timestamp`, `producer_id`,
`run_id`, `related_plan`, and `supersedes`. `timestamp` is a local ordering hint; it is not a
replacement for `generated.at` in a general OKF knowledge bundle.

Read the canonical [OKF v0.2 specification](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md)
before designing a separate knowledge bundle. The [okf-skills toolkit](https://github.com/scaccogatto/okf-skills)
is a useful reference for deterministic validation, lifecycle-only logs, progressive indexes,
trust/lifecycle display, and backfill guardrails.

## What belongs here

Use the bundle for information that helps a later agent resume safely:

- a session handoff with verified state, open threads, and the next action;
- a decision with alternatives, rationale, and consequences;
- a meaningful progress checkpoint tied to a plan, issue, branch, or commit;
- a distilled subagent finding and its disposition;
- verification evidence with the exact gate, result, limits, and follow-up;
- a parallel lane registration when ownership or external runtime linkage must survive a merge.

Do not use the bundle as the authority for:

- architecture or product contracts that belong in ADRs and architecture guides;
- active task claiming, TODO queues, or mutable workstream manifests;
- raw terminal output, session transcripts, benchmark dumps, or generated artifacts;
- a changelog for every edit or a diary of every agent turn;
- a complete mirror of a repository's existing Markdown documentation.

The source document remains authoritative. Memory should link to it and summarize only the
continuity-relevant conclusion.

## Capture budget

Before writing a shard, ask: **What could a future agent do incorrectly if this fact disappeared?**
If the answer is unclear, do not write a record.

Use these defaults:

| Boundary | Capture policy |
| --- | --- |
| Plan selected | Register the lane or create one progress record if the plan is not already discoverable. |
| Routine implementation | No record unless the approach, ownership, or next action changes. |
| Verification | Combine related commands and limits into one `Verification Evidence` record. |
| Commit | Record only a durable transition, migration boundary, or recovery fact. The commit itself is already in Git. |
| Context compaction or handoff | Create one `Session Handoff` with the next action and unresolved risks. |
| Blocker or reversal | Create one progress, decision, or finding record explaining the change. |
| Lifecycle event | Use `log` only for creation, deprecation, supersession, regeneration, migration, or verification. |

One registration lineage is enough for one lane. A successor snapshot is justified when the lane's
status, claim, owner, branch, plan, handoff, or integration relationship changes. Do not create a
successor for every test command or conversational turn.

## Canonical order and views

The bundle has four layers:

1. Immutable concept shards are canonical facts.
2. Registration snapshots publish lane identity and causal state.
3. `current-state.md` and `log.md` are deterministic materialized views.
4. `index.md` is stable progressive-disclosure navigation.

The current renderer applies two noise controls:

- `current-state.md` lists only open registration heads; completed or cancelled history remains in
  the shards but does not look active.
- `log.md` lists only `Memory Event` shards whose `event_kind` is a lifecycle kind. Work progress,
  verification documents, and routine events remain discoverable from their own directories and
  the recent-evidence section.

If a rollup is stale or conflicts, preserve all shards and regenerate the view after integrating
Git state. Do not make a rollup the write target for normal work.

## Concurrent writes

The protocol is a merge protocol, not a lock:

- every normal fact gets a unique `record_id` and exclusive-create path;
- timestamps help scanning but do not establish causality;
- `supersedes` records causal lineage for registration snapshots;
- a successor may supersede only snapshots from the same `registration_id`;
- an integration owner resolves competing heads with a new successor snapshot;
- external `WORKSTREAM.json`, `TODO`, and `HANDOFF` files remain mutable runtimes owned by their
  workflow, and are referenced rather than copied or edited by this skill.

Read [the concurrent-write protocol](concurrent-writes.md) for the full invariant and migration
rules.

## Curated OKF knowledge versus engineering memory

These are complementary, not interchangeable:

| Need | Recommended surface |
| --- | --- |
| Recover a half-finished task | Engineering memory shard |
| Explain a stable architecture boundary | ADR or architecture guide, optionally linked from a concept |
| Discover services, packages, APIs, schemas, or runbooks | A curated OKF bundle with one concept per domain entity |
| Track active ownership | Workstream runtime or issue tracker, linked by a registration |
| Prove a test or release gate | Verification Evidence plus the owning test/report |

A curated OKF bundle should use `generated`, `verified`, `status`, `stale_after`, and `sources`
when those facts are known. It should add directory `index.md` files for progressive disclosure,
use standard Markdown links, and record per-claim provenance with `sources[].id` footnotes where
useful. It should not turn routine Git history into concepts.

## Applying this to large repositories

For a fast-moving, mature repository:

1. Keep the memory root narrow and treat existing architecture, release, plan, and workstream
   directories as the owning sources.
2. Capture only current lanes, meaningful decisions, handoffs, and verification boundaries.
3. Let completed registration snapshots and old evidence remain historical; do not render them as
   active state and do not put them in the lifecycle log unless they represent a lifecycle event.
4. If discovery is poor, create a small curated index or OKF overlay for the highest-value concepts;
   do not mass-convert every Markdown file.
5. Validate the managed bundle, not an unrelated mixed directory containing legacy reports or
   ordinary documentation.

This is especially important when a project has accumulated hundreds of historical registrations,
progress notes, or verification files. The remedy is capture policy and view compaction first, not
automatic deletion. Deleting old shards is a separate repository decision that must preserve links,
Git history, and any accepted source-of-truth boundary.

## Migration procedure

For an existing bundle:

1. Run `git status --short --branch` and inspect the bundle without modifying it.
2. Run `init` to add missing structure; it does not overwrite root views.
3. Preserve human-maintained root views with `render --owner <id> --adopt-rollups` before derived
   rendering takes ownership.
4. Create a new registration lineage only for currently relevant lanes. Do not recreate every old
   session or task as an active lane.
5. Keep old shards as history. Use the sparse renderer to make current state and lifecycle history
   readable.
6. Validate and review warnings. Fix new records first; migrate old records only in an explicit,
   separately reviewable change.

For a repository whose documentation directory is mixed or only partly frontmattered, create a
dedicated managed bundle (for example `.okf/` or a clearly scoped knowledge subdirectory) and link
back to existing documents. Do not run a strict bundle validator over the entire documentation tree
unless the project has intentionally adopted every Markdown file there as an OKF concept.

## Validation limits

`wiki_memory.py validate` checks the engineering-memory profile: frontmatter type presence,
duplicate IDs, conflict markers, registration lineage, stale derived views, unsafe local paths,
oversized rollups, and external runtime drift. It is not a full YAML or OKF v0.2 validator.

Use an upstream OKF validator when a bundle is intended for general OKF exchange. Treat warnings as
migration guidance, but never ignore unresolved structural errors or a broken registration lineage
before rendering shared views.

## Sources

- Google Cloud, [Open Knowledge Format v0.2](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md)
- GoogleCloudPlatform, [Open Knowledge Format repository](https://github.com/GoogleCloudPlatform/open-knowledge-format)
- scaccogatto, [okf-skills toolkit](https://github.com/scaccogatto/okf-skills)

# Architecture Maps

This directory maps durable capability areas for agentic development. Use it for large Rust projects
where architecture boundaries, workstream selection, and multi-terminal ownership matter.

Architecture maps are not task ledgers. Keep task status, evidence, and closeout details in
`docs/workstreams/<slug>/`.

## Files

- `LANES.md`: optional registry for long-lived architecture lanes such as storage, transcode,
  playback, realtime, or admin.
- `<CAPABILITY>.md`: optional deep dive for one capability area.

## Authority

1. Accepted ADRs define hard-to-change decisions.
2. Architecture maps explain capability boundaries, risks, and proposed workstreams.
3. Workstreams own execution details, gates, evidence, and handoff state.

## Linkage Rules

- Link active or proposed workstreams from the relevant architecture map.
- Add `architecture_refs`, `capability_tags`, and `lane_slug` to `WORKSTREAM.json` when they apply.
- Do not duplicate workstream evidence here.

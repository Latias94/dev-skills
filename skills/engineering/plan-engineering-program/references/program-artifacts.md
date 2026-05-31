# Program Artifacts

Use this when deciding where state belongs.

## Authority

1. `docs/adr/`: hard-to-change contracts and accepted architecture decisions.
2. `docs/architecture/`: lane map, ownership, shared scopes, target maturity, and roadmaps.
3. `docs/workstreams/`: executable durable slices with design, tasks, evidence, gates, and handoff.
4. `CONTEXT.jsonl`: context manifests for lane terminals and reviewers.
5. `.codex/planner-state.local.json`: local runtime pointers only; never architecture truth.
6. Chat/session JSONL: recovery hint only.

## Recommended Lane Doc Shape

Each major lane should have either a dedicated doc or a clear section in `LANES.md`:

- lane purpose and non-goals,
- owned crates/modules/files,
- shared scopes and required approvals,
- current state and target maturity,
- active/draft/deferred/blocked workstreams,
- campaign queue and next medium goals,
- validation ladder from narrow tests to integration gates,
- related repo responsibilities,
- autonomy policy for lane terminals.

## Workstream Pressure Rule

Do not create a workstream for every idea. Keep early candidates in the lane backlog. Open or reuse a
workstream only when the slice has a durable goal, scope boundary, validation path, and closeout
criteria.

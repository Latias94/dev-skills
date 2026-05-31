# Program Artifacts

Use this when deciding where state belongs.

## Authority

1. `docs/adr/`: hard-to-change contracts and accepted architecture decisions.
2. `docs/architecture/`: lane map, ownership, shared scopes, target maturity, and roadmaps.
3. `docs/workstreams/`: executable durable slices with design, tasks, evidence, gates, and handoff.
4. `CONTEXT.jsonl`: context manifests for lane terminals and reviewers.
5. `.codex/planner-state.local.json`: local runtime pointers only; never architecture truth.
6. Chat/session JSONL: recovery hint only.

## Field-Level Authority

- `LANES.md` owns lane routing, ownership, shared scopes, and intended active queue.
- `WORKSTREAM.json.current_task` plus `TODO.md` own executable task state.
- `EVIDENCE_AND_GATES.md` owns validation claims.
- `HANDOFF.md` and `JOURNAL/` explain recovery context, but do not override task state.
- README prose is discoverability, not task authority.

If these disagree, mark the conflict as docs drift. Prefer a mechanical repair recommendation when
the correct value is obvious from `TODO.md`, `WORKSTREAM.json`, and evidence; otherwise put the
decision in `Minimal User Input Needed`.

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

## Legacy Substrate Repair

When a large repo already has workflow docs, check for drift before assigning work:

- `LANES.md` active queue disagrees with `WORKSTREAM.json.current_task`,
- old terms such as `planner-approved` or one-task-only lane protocols conflict with campaign goals,
- `WORKSTREAM.json.status` uses non-canonical values such as `complete` or `completed`,
- active workstreams lack `lane_slug`, architecture refs, context manifests, or gates.

Treat these as hygiene findings. Repair only when the fix is mechanical and in scope; otherwise
report the migration recommendation before starting more implementation.

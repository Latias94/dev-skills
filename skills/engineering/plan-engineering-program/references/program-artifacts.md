# Program Artifacts

Use this when deciding where state belongs.

## Authority

1. `docs/product/`: product intent, MVP ladder, non-goals, capability pressure, and priority class.
2. `docs/adr/`: hard-to-change contracts and accepted architecture decisions.
3. `docs/architecture/`: lane map, ownership, shared scopes, target maturity, and roadmaps.
4. `docs/workstreams/`: executable durable slices with design, tasks, evidence, gates, and handoff.
5. `CONTEXT.jsonl`: context manifests for lane terminals and reviewers.
6. `.codex/planner-state.local.json`: local runtime pointers only; never architecture truth.
7. Chat/session JSONL: recovery hint only.

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

## Program Control Loop

Use these states when reporting program progress:

1. `DISCOVERY`: initial read-only evidence gathering before shaping or planning.
2. `SHAPE`: product/MVP/capability decisions are not ready for engineering campaigns.
3. `PLAN`: lane map, workstreams, ADR candidates, or campaign queue need design.
4. `ASSIGN`: a lane campaign or bundle is ready to hand to a terminal.
5. `EXECUTE`: lane terminal is running an approved bundle or campaign.
6. `INTAKE`: worker/lane output is being reconstructed from git, docs, and session tails.
7. `VERIFY`: reviewer/verifier is checking scope, code quality, and fresh gates.
8. `INTEGRATE`: accepted work is committed, synced, merged, or sequenced.
9. `RECON`: planner is doing read-only discovery for the next campaign while lanes run.
10. `DECISION`: product, ADR, side-effect, or cross-repo decision cannot be inferred safely.

Do not skip from `EXECUTE` to `ASSIGN`; pass through `INTAKE` and `VERIFY`. Do not let `RECON`
mutate active ledgers underneath workers.

## Workstream Pressure Rule

Do not create a workstream for every idea. Keep early candidates in the lane backlog. Open or reuse a
workstream only when the slice has a durable goal, scope boundary, validation path, and closeout
criteria.

## Closed History Rule

Closed, complete, or completed workstreams are historical evidence. They may identify prior
decisions, validated gates, and follow-on candidates, but they are not an active queue. Summarize
closed history by lane/capability before proposing new work. Limit extracted follow-ons to the
strongest two or three per candidate lane and cross-check each against current code pressure, ADRs,
crate boundaries, and validation gates.

## Legacy Substrate Repair

When a large repo already has workflow docs, check for drift before assigning work:

- `LANES.md` active queue disagrees with `WORKSTREAM.json.current_task`,
- old terms such as `planner-approved` or one-task-only lane protocols conflict with campaign goals,
- `WORKSTREAM.json.status` uses non-canonical values such as `complete` or `completed`,
- active workstreams lack `lane_slug`, architecture refs, context manifests, or gates.

Treat these as hygiene findings. Repair only when the fix is mechanical and in scope; otherwise
report the migration recommendation before starting more implementation.

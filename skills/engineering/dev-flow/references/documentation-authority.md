# Documentation Authority

Use this when a skill must decide whether to update workstream docs, architecture docs, ADRs,
context, evidence, or only journal/handoff notes.

## Authority Layers

| Artifact | Purpose | Update when | Who should update |
| --- | --- | --- | --- |
| `docs/adr/` | Accepted long-term contracts and hard-to-change decisions | Public contracts, storage formats, cross-lane seams, protocols, compatibility, security, or deployment behavior changes | Upper planner/docs role after user decision |
| `docs/architecture/` | Current architecture maps, lane registry, ownership scopes, and module relationships | Code structure or lane ownership changed without needing a new decision | Upper planner or architecture-lane terminal with approval |
| `docs/workstreams/<slug>/DESIGN.md` | Target state, non-goals, and execution contract for one durable lane | Workstream target, scope, or non-goals change | Upper planner only |
| `TODO.md` | Task ledger for executable slices | Task ownership, status, dependencies, or validation changes | Upper planner; workers update only their assigned task status/notes |
| `EVIDENCE_AND_GATES.md` | Validation gates and command evidence | A gate is added, skipped, failed, or freshly proven | Worker/verifier for their scope |
| `CONTEXT.jsonl` | Manifest of docs/files required before editing | Workers need new ADRs, architecture docs, evidence, or research in scope | Upper planner |
| `CONTEXT.md` | Domain language and glossary | A durable domain term is added or clarified | Grill/docs/upper planner role |
| `JOURNAL/` and `HANDOFF.md` | Session continuity | Work may be resumed by another agent | Worker/lane/upper planner |
| `.codex/planner-state.local.json` | Local runtime state | Terminals, worktrees, branches, bundles, or sessions change | Upper planner/integrator only; never committed |

## Decision Rules

- If a worker discovers the task changes an ADR, architecture target state, or shared contract,
  report `BLOCKED` or `NEEDS_CONTEXT`; do not rewrite the decision in place.
- If implementation changed current structure but not a hard decision, update architecture docs or
  ask the planner to do so.
- If task scope, done criteria, or ownership changed, update the workstream task ledger before
  assigning more work.
- If validation changed, update evidence even when code does not change.
- If a journal contains durable knowledge, promote it into an ADR, architecture doc, workstream doc,
  or context glossary before closeout.
- If an ADR and a workstream disagree, ADR wins unless the planner explicitly proposes reopening it.

## Skill Responsibilities

- `audit-project-scale`: identify stale docs and recommend repair; do not invent decisions.
- `grill-with-docs`: update `CONTEXT.md` and propose ADRs as decisions crystallize.
- `plan-architecture-lane`: choose whether docs are sufficient, need code-aware planning, or need an
  architecture review before workstreams.
- `open-workstream`: create or reuse workstream docs and context manifest.
- `plan-engineering-program`: update lane maps, campaign queues, and planner-owned runtime state;
  route ADR or architecture-doc changes to the right role.
- `integrate-lane-results`: inspect completed lane output, route review/verify, and update
  integration/sync state.
- `run-workstream-task`: update assigned task notes, evidence, journal, and handoff only.
- `review-workstream`: flag stale or missing docs; do not fix them during review.
- `verify-rust-workstream`: update evidence for fresh command results.
- `close-workstream`: ensure durable outcomes are promoted out of journals before closeout.

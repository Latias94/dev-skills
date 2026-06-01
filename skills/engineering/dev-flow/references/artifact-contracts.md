# Artifact Contracts

Use this when deciding whether orchestration state is real enough to assign work.

An artifact is useful only when its shape, owner, lifecycle, and consumers are explicit. A
well-written file that no skill or script reads is narrative, not control state.

## Catalog

| Artifact | Shape | Owner | Consumers | Gate |
| --- | --- | --- | --- | --- |
| `WORKSTREAM.json` | JSON object | planner | planner, lane, integrator | required for durable workstreams |
| `DESIGN.md` | Markdown contract | planner | worker, reviewer | required before broad execution |
| `TODO.md` | Markdown task ledger | planner | worker, reviewer, integrator | must match `TASKS.jsonl` |
| `TASKS.jsonl` | one JSON object per task | planner/integrator | scripts, worker, reviewer | required before assignment |
| `CAMPAIGNS.jsonl` | one JSON object per campaign | planner/integrator | lane terminal, integrator | required for auto-advance |
| `CONTEXT.jsonl` | one JSON object per context target | planner | worker, reviewer | required when context is non-trivial |
| `EVIDENCE_AND_GATES.md` | Markdown evidence ledger | verifier/integrator | reviewer, closer | required before completion |
| `HANDOFF.md` | Markdown continuation note | current owner | next owner | recovery hint only |
| `JOURNAL/*.md` | dated Markdown notes | current owner | integrator | recovery hint only |
| `.codex/planner-state.local.json` | local JSON | upper planner | upper planner only | never commit personal paths |

## Invariants

- `TODO.md` explains intent; `TASKS.jsonl` carries parseable task state. Neither replaces the other.
- `CAMPAIGNS.jsonl` may reference only task IDs that exist in `TASKS.jsonl`.
- Campaigns with auto-advance must state gates, checkpoints, stop conditions, and a side-effect
  policy from `side-effect-policy.md`.
- `WORKSTREAM.json.current_task` must be `null` or reference a task in `TASKS.jsonl`.
- `CONTEXT.jsonl` lists durable docs and research artifacts, not files a worker is expected to edit.
- `EVIDENCE_AND_GATES.md` records claims and command evidence; chat and session tails do not.
- Personal runtime facts belong in `.codex/planner-state.local.json`, not committed workstream docs.

## Lifecycle

1. `draft`: planner creates design, task ledger, context manifest, gates, and optional campaigns.
2. `active`: assignment gate passes and at least one task or campaign is ready.
3. `running`: a terminal owns an approved task, bundle, or campaign.
4. `review`: output exists but has not passed contract and code-quality review.
5. `verify`: review is acceptable but fresh command evidence is still required.
6. `integrated`: accepted output and machine-readable state are reconciled.
7. `closed`: closeout gates pass and follow-ons are split or deferred.

## Drift Policy

When artifacts disagree, stop implementation assignment and classify the drift:

- Mechanical drift: obvious mismatch that can be repaired from current docs and evidence.
- Authority drift: two authoritative artifacts disagree and planner judgment is needed.
- Decision drift: product, ADR, public contract, or side-effect policy changed and user input is needed.

Repair drift in `PLAN` or `INTAKE`. Do not let a worker choose between conflicting sources while
implementing.

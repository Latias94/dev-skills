# Production Control

Use this when a large repo has multiple agents, worktrees, or campaigns. The objective is not more
activity; it is more accepted integrated work per unit of user attention.

## Operating Metric

Track these when planning or reviewing a campaign:

| Metric | Why it matters |
| --- | --- |
| Autonomy horizon planned vs actual | Shows whether goals are too tiny or too vague |
| User interruptions per campaign | Measures user-attention cost |
| `DONE` to accepted integration time | Exposes review/verify/integration bottlenecks |
| Failed gates and reruns | Exposes weak readiness or validation selection |
| Merge conflicts and branch age | Exposes over-parallelism and stale worktrees |
| Active terminals and WIP count | Exposes half-finished work accumulation |
| Integrated slices per campaign | Measures throughput that actually reached main |

If a workflow change improves documentation but not these metrics, treat it as unproven.

## WIP Limit

- Default active lane/worker terminal budget: three, excluding the upper planner.
- When three terminals are active, prioritize intake, review, verification, sync, merge, and closeout
  before opening another lane.
- A lane with dirty, unreviewed, or unverified output should not receive more implementation work.
- Prefer one serial campaign over several blocked terminals when tasks share hot files or contracts.

## Assignment Go/No-Go

Only assign implementation when all are true:

- lane map or explicit temporary lane map exists,
- active/draft/ready workstream or bundle exists,
- TODO, gates, source scope, and branch/worktree agree,
- owned scopes and shared scopes are explicit,
- ADR/schema/public-contract risks are classified,
- validation gate is runnable,
- autonomy horizon and stop conditions are stated.

If any item is missing, use `DISCOVERY`, `PLAN`, or read-only `RECON`, not `ASSIGN`.

## Post-Blocker Planning

When the user approves blocker clearing, substrate repair, queue reconciliation, closeout, or
read-only recon, the terminal must return to the planning question before starting implementation:

- what blocker was removed,
- whether parallelism is now possible,
- which blockers still prevent parallelism,
- three to five candidate directions when evidence supports them,
- terminal budget and WIP count,
- recommended `ASSIGN`, serial campaign, or further `PLAN`/`RECON`.

Do not finish a repair step by silently starting the next task. If only one task is ready, say why
parallel work is still blocked and propose a serial campaign or single bounded goal.

## Campaign State Record

When local planner state is used, keep it machine-readable and local-only:

```json
{
  "state": "DISCOVERY|SHAPE|PLAN|ASSIGN|EXECUTE|INTAKE|VERIFY|INTEGRATE|RECON|DECISION",
  "lane": "storage",
  "worktree": "F:/SourceCodes/Rust/nako-worktrees/nako-storage",
  "branch": "lane/storage-campaign-20260601",
  "autonomy_horizon": "90 min / 3 bundles",
  "side_effect_policy": "manual|auto-commit-sync|auto-commit-sync-merge",
  "gates": ["cargo nextest run -p crate filter"],
  "stop_conditions": ["failed gate", "shared scope", "ADR change", "dirty unrelated files"]
}
```

Do not commit personal absolute paths. Project docs remain the architecture authority.

## Integration Cadence

- Commit accepted slices at task/bundle boundaries when policy allows it.
- Sync main into active lane worktrees after accepted commits or before starting a dependent slice.
- Merge shared-scope or dependency-unlocking work earlier than isolated lane-local work.
- Run a post-merge gate before declaring integration complete.
- Old branches and long-lived dirty worktrees are WIP debt; route them to integration before
  starting new work.

## Build And Disk Cost

- Prefer one stable worktree per lane, not one worktree per workstream.
- Do not create a new worktree until terminal budget, branch purpose, and cleanup point are clear.
- Consider Rust `target/` growth and repeated build cost when proposing lane count.
- Close or retire inactive worktrees during integration/closeout planning.

## Failure Review

Run a short workflow review when a campaign ends with repeated user interruptions, failed gates,
merge conflicts, or `DONE_WITH_CONCERNS`. Record whether the failure came from scope, docs,
validation, state, or side-effect policy, then update the next campaign plan.

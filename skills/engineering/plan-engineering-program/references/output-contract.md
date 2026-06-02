# Program Output Contract

Use this when preparing upper-planner output, campaign plans, terminal prompts, or live experiment
handoffs.

## Opening Block

Start with:

```md
## Program Action
Mode: DISCOVERY | SHAPE | PLAN | ASSIGN | RECON | DECISION
Operating Mode: READINESS | AUDIT
Now: <what this commander terminal should do next>
Why: <one sentence grounded in repo evidence>
```

Always include:

- `Implementation Horizon: <N>`
- `Product RECON Horizon: <N>` when product capability candidates are detected
- whether blockers are `active-queue blockers` or `historical audit findings`
- whether the next move is safe `read-only inspection`, `artifact repair`, or `assignment`

When running in `AUDIT`, do not collapse historical evidence drift into "nothing is assignable"
unless the active queue itself is affected.

## Planning Payload

After the opening block, include only sections justified by current repo evidence:

- recommended action and phase,
- evidence read,
- lane map changes,
- terminal budget and WIP count,
- metrics and `Autonomy Horizon`,
- campaign candidates,
- parallelism or serial-campaign decision,
- required docs or ADR updates,
- proposed side-effect policy,
- worktree recommendations,
- exact Codex goals to set after approval,
- `Minimal User Input Needed` with only decisions that cannot be inferred from repo evidence.

## Terminal Prompt Requirements

Every lane or worker prompt must include:

- assigned task, bundle, campaign, or lane scope,
- required context files,
- owned and shared scope,
- validation gates,
- side-effect policy and stop conditions,
- expected evidence updates,
- final status marker: `DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT`,
- changed files,
- validation results,
- concerns and follow-ups,
- review/verify readiness,
- `WORKSTREAM_RESULT:` from `../../dev-flow/references/agent-contracts.md`,
- instruction to return to `integrate-lane-results`.

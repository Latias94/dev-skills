# Planner Report States

Use this when the planner reports to the user. The report shape depends on the planner mode, but
every report must start with the current planner action so the user knows what happens next.

Do not default to HTML. Use Markdown tables for scan-heavy state, numbered candidates for
architecture findings, and fenced prompts for copy/paste terminal work. Use HTML only for a durable
dashboard or artifact the user explicitly wants.

## Common Header

Every planner report starts with:

```md
## Planner Action
Mode: <mode>
Now: <what this planner terminal should do next>
Why: <one sentence grounded in repo evidence>
```

Then include only the sections that fit the mode. Do not pad the report with empty headings.

## Modes

### 1. `DISCOVERY`

Use when no current workstream or lane is known.

Include:

- candidate workstreams/lanes table,
- missing context or stale docs,
- recommendation: audit, plan lane, reuse/open workstream, or stay lightweight,
- side-effect approvals needed before creating worktrees or branches.

### 2. `ASSIGNMENT`

Use when the planner is about to publish tasks, lane bundles, or terminal prompts.

Include:

- lane bundle table: lane, worktree, workstream/bundle, owned scope, shared scope, gate,
- exact Codex goal text for each approved bounded task, bundle, or campaign,
- terminal prompts,
- stop conditions,
- approvals before worktree/branch/shared-scope side effects.

### 3. `RUNNING_STATUS`

Use when terminals are already working and the user asks for status.

Include:

- worktree/lane table: path, branch, current work, state, blocker, next owner,
- review/verify/integration queue,
- which lanes may continue, wait, or sync,
- whether this planner should do idle read-only architecture reconnaissance while workers run.

### 4. `RESULT_INTAKE`

Use after a worker/lane terminal reports `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, or
`NEEDS_CONTEXT`.

Include:

- inspected worktree, branch, dirty state, changed scope,
- claimed status and planner classification,
- next action: review, verify, fix prompt, split follow-on, close, or block,
- prompt to paste back to the worker or reviewer,
- reminder that worker `DONE` is not accepted completion.

### 5. `REVIEW_VERIFY`

Use when the planner or reviewer is checking completed work.

Include:

- review findings first, ordered by severity,
- required fresh verification gates,
- accepted risks or missing evidence,
- whether the planner now verifies, asks a reviewer, or returns a fix prompt.

### 6. `INTEGRATION_SYNC`

Use when reviewed and verified work is ready to commit, merge, or sync.

Include:

- accepted slice and evidence,
- exact commit/merge/sync plan,
- branches/worktrees affected,
- side-effect approvals still required,
- next Codex goal or lane bundle after integration.

### 7. `IDLE_RECON`

Use when workers are running and the planner can perform read-only architecture reconnaissance.

Include architecture candidates in the `improve-codebase-architecture` style:

- **Files**,
- **Problem**,
- **Solution**,
- **Benefits** in locality, leverage, and testability terms,
- readiness: `IMPLEMENT_NOW`, `PLAN_FIRST`, `ADR_FIRST`, `WAIT_FOR_ACTIVE_BRANCH`, or `DEFER`,
- suggested lane/workstream owner.

Do not mutate active ledgers or ADRs in this mode. Convert findings into proposed candidates or
approval questions.

### 8. `BLOCKED_DECISION`

Use when progress needs user input, ADR choice, schema/contract choice, related-repo decision, or
failed-gate judgment.

Include:

- blocking fact,
- options with tradeoffs,
- recommended choice,
- what remains paused until the decision is made.

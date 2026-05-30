# Multi-Agent Flow

## Roles

**Planner**
: Owns the workstream, task ledger, lane goal bundles, dependency order, and conflict resolution.

**Architecture Lane Terminal**
: Owns one capability area across a sequence of workstreams, such as storage, transcode, playback,
or admin. It should use `run-architecture-lane`.

**Worker**
: Owns one bounded task from the ledger.

**Reviewer**
: Checks implementation against both repository standards and workstream intent.

## Launch Criteria

Use multiple agents only when:

- tasks or architecture lanes are independent enough to run in parallel,
- file scopes are disjoint or clearly serialized,
- validation can be run per task,
- and the planner can integrate results.

Keep the work local when the next step depends on one unresolved design decision.

## Parallel Work Pattern

1. Planner updates `TODO.md` with task IDs, owners, dependencies, scopes, validation, and required
   context.
2. Planner prepares `CONTEXT.jsonl` when the workstream will use lane terminals or parallel
   workers.
3. Planner creates a lane goal bundle when a long-running terminal should keep working.
4. Each worker receives one task ID and an explicit file/module scope.
5. Workers update only:
   - their task status,
   - relevant evidence notes,
   - a journal entry or handoff.
6. Planner integrates results and resolves conflicts.
7. Reviewer uses `review-workstream` for contract and code-quality checks.
8. Planner uses `verify-rust-workstream` before accepting completion.

## Architecture Lane Pattern

Use architecture lanes when the same terminal should keep advancing a capability area over multiple
workstreams.

1. Assign one lane per terminal, such as `storage`, `transcode`, or `playback`.
2. Give the terminal a lane goal bundle: one to three ready tasks, context manifest, validation, and
   stop conditions.
3. Record owned scopes and shared scopes. Shared scopes require planner coordination.
4. Keep the terminal/worktree stable, but prefer one short-lived branch per workstream.
5. Close and verify the current workstream before starting the next queued workstream.
6. Stop the lane terminal when the bundle is done, blocked, missing context, or touches shared
   scope.

## Lane Goal Bundle Sizing

Use a bundle when Codex should run for longer than one small task without constant user switching.
The bundle should be:

- bigger than a single mechanical edit,
- smaller than a whole architecture area,
- limited to one lane and one stable worktree,
- backed by `TODO.md` task IDs and a context manifest,
- validated by commands the lane terminal can run,
- stopped by clear blockers or shared-scope changes.

If the user wants a Codex goal, bind it to the bundle or one bounded task, not to the whole lane.

## Worker Prompt Shape

```text
You are Worker <id>. You are not alone in the codebase.
Own task <TASK-ID> from docs/workstreams/<slug>/TODO.md.
Do not rewrite global scope or unrelated tasks.
Do not revert user or other worker changes.
Touched file scope: <paths>.
Required context: <CONTEXT.jsonl entries or task-specific docs>.
Validation: <commands>.
Final status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT.
Final response: changed files, validation, evidence updates, concerns, next notes.
```

## Worker Status Protocol

- `DONE`: implementation and task-local validation completed.
- `DONE_WITH_CONCERNS`: completed, but reviewer/planner should inspect named concerns before accepting.
- `BLOCKED`: cannot finish without task split, design change, or external input.
- `NEEDS_CONTEXT`: needs missing repo, workstream, or requirement context before continuing.

## Stop Conditions

Stop and escalate to the planner when:

- the task requires changing an ADR or workstream target state,
- another worker owns the same file region,
- validation is impossible with the current task split,
- or the implementation reveals the task is the wrong vertical slice.

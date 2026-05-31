# Status And Next Action

Use this when the user asks for status, progress, "what now", terminal allocation, or whether a
worker/lane result should continue. This is a planner mode; do not implement worker tasks here.

## Inspect

- current repo and related repo `git status --short --branch`,
- `git worktree list` and branch/head for active worktrees,
- active `WORKSTREAM.json` files, `TODO.md`, `HANDOFF.md`, and `EVIDENCE_AND_GATES.md`,
- lane registry, planner state, and context manifests when present,
- terminal reports when available,
- `scripts/session_tail_for_worktree.py <worktree>` as lightweight supplementary context for active
  worktrees, especially when report/state is stale or missing,
- session refs only as recovery pointers.

## Classify

- `RUNNING`: terminal is still inside an approved task, lane bundle, or lane campaign.
- `ACCEPT_FOR_REVIEW`: worker/lane reports done; planner should review before accepting.
- `NEEDS_VERIFY`: review is acceptable but fresh gate evidence is missing.
- `READY_TO_INTEGRATE`: reviewed, verified, scoped, and ready for commit/merge planning.
- `READY_FOR_NEXT_BUNDLE`: current bundle is accepted and the same lane has a ready queued bundle.
- `NEEDS_FIX`: return a bounded fix prompt to the same worker/lane terminal.
- `BLOCKED`: user, ADR, shared-scope, schema, cross-repo, or failed-gate decision required.

## Output Shape

Use `planner-report-states.md` and report mode `RUNNING_STATUS` unless the evidence shows the
planner should switch to `RESULT_INTAKE`, `REVIEW_VERIFY`, `INTEGRATION_SYNC`, `IDLE_RECON`, or
`BLOCKED_DECISION`.

Lead with the current planner action, then provide:

- worktree/lane table: path, branch, task/bundle, state, blocker, next owner,
- review/verify/integration queue,
- lane bundle, campaign step, or task that may continue next,
- exact prompt to paste into each terminal,
- Codex goal text to set only for approved bounded work,
- side-effect approvals needed before creating worktrees, committing, merging, pushing, or syncing.

Use current-terminal wording. If the planner should review or verify now, say "Planner now reviews"
or "Planner now verifies" instead of "ask planner/reviewer".

## Decision Rules

- Worker `DONE` is not completion; default next action is planner review, then fresh verification.
- Do not start a next bundle when failed gates, `DONE_WITH_CONCERNS`, shared-scope conflicts, or
  missing evidence affect that lane.
- If the lane queue is empty but the user wants continued deepening, return to
  `plan-architecture-lane` to refresh the lane backlog before assigning more work.
- If a lane campaign is pre-approved, let the lane terminal auto-advance only through listed steps
  whose gates pass and whose stop conditions do not trigger.
- Never treat a recovered last message as completion. Use it to decide which repo evidence, review,
  verification, or follow-up prompt is needed.

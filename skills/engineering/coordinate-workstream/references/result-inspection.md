# Result Inspection Mode

Use this when the user asks the planner to inspect a lane terminal, worker terminal, branch, or
worktree result and decide what should happen next.

## Inputs

- worktree path or branch,
- workstream path and task/bundle ID if known,
- terminal final report if available,
- session id only when the report or docs are missing,
- related repo paths when the change spans repositories.

## Read

Prefer repo evidence over chat:

- `git status --short --branch`,
- `git diff --stat` and `git diff --name-status`,
- relevant changed files when needed,
- `TODO.md`, `EVIDENCE_AND_GATES.md`, `HANDOFF.md`, and latest useful `JOURNAL/*.md`,
- validation evidence named by the terminal report,
- optional `codex-session-recovery` summary when the user gives a session id.

## Decisions

Classify the result:

- `ACCEPT_FOR_REVIEW`: scope and evidence look ready for `review-workstream`.
- `NEEDS_FIX`: implementation or docs are incomplete.
- `NEEDS_VERIFY`: review is acceptable but fresh evidence is missing.
- `BLOCKED`: shared scope, ADR, schema, or user decision is required.
- `READY_FOR_NEXT_BUNDLE`: reviewed and verified; planner can propose the next approved bundle.

## Output

Report scope fit, touched files, validation, evidence status, concerns, required review/verify step,
merge/sync advice, whether a follow-up should be split, next approved task or bundle, Codex goal to
set, and terminal prompt. Do not let a worker choose the global next task.

Start with the current planner terminal's next action. If review or fresh verification is the next
step, say whether the current planner will do it or whether a separate reviewer/verifier terminal is
being assigned. Do not phrase this as "let planner/reviewer accept" when the current terminal is the
planner; say "Planner now reviews..." or "Send this prompt to Reviewer terminal...".

When a worker terminal needs action, provide a pasteable prompt for that terminal. When a worker's
result is ready for review, tell that worker to stand by for review fixes and not start the next
task until the planner accepts the result.

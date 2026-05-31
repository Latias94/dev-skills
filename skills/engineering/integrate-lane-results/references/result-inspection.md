# Result Inspection Mode

Use this when the user asks the integrator or upper planner to inspect a lane terminal, worker terminal, branch, or
worktree result and decide what should happen next.

## Inputs

- worktree path or branch,
- workstream path and task/bundle ID if known,
- terminal final report if available,
- optional worktree session tail as lightweight supplementary context,
- session id when the user provides one or deeper recovery is needed,
- related repo paths when the change spans repositories.

## Read

Prefer repo evidence over chat:

- `git status --short --branch`,
- `git diff --stat` and `git diff --name-status`,
- relevant changed files when needed,
- `TODO.md`, `EVIDENCE_AND_GATES.md`, `HANDOFF.md`, and latest useful `JOURNAL/*.md`,
- validation evidence named by the terminal report,
- optional `scripts/inspect_worktree_result.py <worktree> --json` to combine git state, the latest
  visible assistant message, and workstream docs into result-intake evidence,
- optional `scripts/session_tail_for_worktree.py <worktree>` when only the latest visible message is
  needed,
- optional `codex-session-recovery` summary when the user gives a session id or the tail is not
  enough.

Use recovered session text as a hint only. Repo docs, git state, handoff files, and fresh validation
remain authoritative.

## Decisions

Classify the result:

- `ACCEPT_FOR_REVIEW`: scope and evidence look ready for `review-workstream`.
- `NEEDS_FIX`: implementation or docs are incomplete.
- `NEEDS_VERIFY`: review is acceptable but fresh evidence is missing.
- `BLOCKED`: shared scope, ADR, schema, or user decision is required.
- `READY_FOR_NEXT_BUNDLE`: reviewed and verified; the upper planner can propose the next approved bundle.

## Output

Report scope fit, touched files, validation, evidence status, concerns, required review/verify step,
merge/sync advice, whether a follow-up should be split, next approved task or bundle, Codex goal to
set, required documentation updates, and terminal prompt. Do not let a worker choose the global next
task.

Start with the current integration terminal's next action. If review or fresh verification is the next
step, say whether the current integrator will do it or whether a separate reviewer/verifier terminal
is being assigned. Do not phrase this as "let planner/reviewer accept" when the current terminal is
the integrator; say "Integrator now reviews..." or "Send this prompt to Reviewer terminal...".

When a worker terminal needs action, provide a pasteable prompt for that terminal. When a worker's
result is ready for review, tell that worker to stand by for review fixes and not start the next
task until the integrator accepts the result.

Use `../dev-flow/references/documentation-authority.md` when deciding whether the inspected result
needs ADR, architecture-doc, workstream, context, evidence, journal, handoff, or local planner-state
updates. Report the owner for each required update.

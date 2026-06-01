# Side-Effect Policy

Use this when a campaign decides which repo mutations may run without another user prompt. The goal
is fewer interruptions without letting an agent hide risky git operations.

Side-effect policy covers repo-level actions outside normal assigned edits: commits, branch sync,
merge, worktree lifecycle, push, and related-repo mutation. It does not replace the approved task
scope, review, verification, or stop conditions.

## Pre-Approval Scope

A campaign may pre-approve side effects only when the scope is explicit:

- repo and worktree path,
- branch and integration target,
- task, bundle, or campaign ID,
- owned and forbidden/shared file scopes,
- required review and verification gates,
- exact stop conditions,
- allowed policy level,
- optional exact commands for worktree or branch setup.

If any scope item is missing, treat the policy as `manual` for that action.

## Policy Levels

| Policy | May run without another prompt | Still requires a prompt |
| --- | --- | --- |
| `manual` | no git or worktree side effects | commit, sync, merge, worktree create/delete, branch create/delete, push, related-repo mutation |
| `auto-commit` | stage the accepted scope and create a local Conventional Commit | sync, merge, worktree create/delete, branch create/delete, push, related-repo mutation |
| `auto-commit-sync` | `auto-commit`, then sync the approved base branch into the lane worktree when clean | merge, worktree create/delete, branch create/delete, push, related-repo mutation |
| `auto-commit-sync-merge` | `auto-commit-sync`, then merge the accepted lane branch into the approved integration target and run the listed post-merge gate | worktree create/delete, branch create/delete beyond listed exact commands, push, related-repo mutation |

Push is denied by default for every policy. Push may happen only after explicit user approval for
the exact remote, branch, and command.

## Auto-Commit Gate

Do not ask again before committing when all are true:

- the campaign is approved and its policy is `auto-commit`, `auto-commit-sync`, or
  `auto-commit-sync-merge`,
- `WORKSTREAM_RESULT:` exists and matches the task or campaign scope,
- `REVIEW_RESULT:` is `PASS`, or `PASS_WITH_CONCERNS` with non-blocking concerns recorded,
- `VERIFY_RESULT:` is `PASS` with fresh command evidence,
- changed files are inside the approved scope,
- task state, campaign state, and evidence updates are reconciled,
- the worktree has no unrelated dirty files,
- the commit includes only accepted files,
- the commit message is Conventional Commit style and names the task, bundle, or campaign.

Use explicit path staging. Do not use `git add .` in integration.

## Sync And Merge Gates

Sync the approved base branch into a lane worktree only after the accepted slice is committed and
the worktree is clean. Stop on conflicts, unexpected generated files, failed sync gates, or branch
identity mismatch.

Merge an accepted lane branch only when the campaign policy is `auto-commit-sync-merge`, the target
branch is named in the campaign or planner state, and the post-merge gate is listed. Merge one lane
branch at a time. Stop on conflicts, protected branch issues, failed post-merge gates, or target
branch drift.

## Always Stop

Stop in `DECISION` or `BLOCKED_DECISION` before:

- failed review or verification gates,
- unresolved `DONE_WITH_CONCERNS`,
- unrelated dirty files,
- scope expansion beyond the approved task or campaign,
- ADR, schema, public contract, or shared-scope changes that were not already part of the approved
  scope and recorded decision,
- related-repo version, release, or compatibility decisions,
- destructive git commands,
- push operations without exact user approval.

## Reporting

After running side effects, report the executed commands, commit hashes, branches, merge/sync
result, gates run, state files updated, and any skipped action with rationale. Record this in the
`INTEGRATION_RESULT:` marker `side_effects` field.

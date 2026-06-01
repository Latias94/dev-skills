---
name: integrate-lane-results
description: >
  Integrates completed Rust lane, workstream, worker, or worktree results. Use when inspecting
  terminal output, reading worktree/session evidence, deciding review/verify/fix/merge/sync next
  actions, accepting or rejecting DONE/DONE_WITH_CONCERNS/BLOCKED/NEEDS_CONTEXT reports, or
  coordinating branch sync after implementation.
---

# Integrate Lane Results

Use this from the upper architecture / integration terminal after a lane or worker reports progress.
This skill integrates results; it does not discover the next architecture program or implement
worker tasks.

## Read First

If the user names a worktree, branch, workstream, lane, task, bundle, or session, read only what is
needed:

- `git status --short --branch`, `git diff --stat`, `git diff --name-status`
- `WORKSTREAM.json` and relevant lane architecture docs
- `TODO.md`
- `TASKS.jsonl` and `CAMPAIGNS.jsonl` when present
- `EVIDENCE_AND_GATES.md`
- `HANDOFF.md`
- latest relevant `JOURNAL/*.md`
- local planner state when present
- related repo status when the result spans repositories

Use helper scripts before asking the user to paste chat:

- `scripts/inspect_worktree_result.py <worktree> --json`
- `scripts/session_tail_for_worktree.py <worktree>`

Do not make pasted chat the primary evidence path. First combine git state, workstream docs, local
planner state, and session tails. Ask the user only for the missing artifact when no local evidence
can reconstruct the result.

Read the relevant references: result inspection, integration protocol, side-effect approval,
worktree lifecycle, cross-repo coordination, `../dev-flow/references/planner-state.md`,
`../dev-flow/references/artifact-contracts.md`, `../dev-flow/references/agent-contracts.md`,
`../dev-flow/references/gate-taxonomy.md`, `../dev-flow/references/worktree-safety.md`, and
`../dev-flow/references/documentation-authority.md`.

## Process

1. Reconstruct the claimed result from repo evidence, not chat memory.
2. Classify status: `ACCEPT_FOR_REVIEW`, `NEEDS_VERIFY`, `READY_TO_INTEGRATE`, `NEEDS_FIX`,
   `BLOCKED`, or `READY_FOR_NEXT_BUNDLE`.
3. Route review through `review-workstream` and fresh gates through `verify-rust-workstream`.
4. Confirm changed files match the approved lane/task/campaign scope.
5. Identify required documentation and machine-readable state updates using documentation authority.
6. Use bounded revision gates when review or verification fails.
7. Execute approved commit, merge, or sync side effects when a campaign policy allows them;
   otherwise propose exact prompts and ask before side effects.
8. After accepted integration, return the lane to `run-architecture-lane` or the upper planner to
   `plan-engineering-program` for the next campaign.

## Status Rules

- Worker/lane `DONE` is not accepted completion. Review and fresh verification come first.
- `DONE_WITH_CONCERNS` cannot move to the next campaign until concerns are classified.
- Failed gates produce `NEEDS_FIX` or `BLOCKED`, not "mostly done".
- Shared scopes, ADR/schema/contract changes, dirty unrelated files, and cross-repo decisions stop
  integration until the upper planner or user approves.
- A lane terminal may recommend a same-lane next medium goal, but this integration terminal accepts,
  rejects, or routes it; global program sequencing belongs to `plan-engineering-program`.
- Missing `WORKSTREAM_RESULT:`, `REVIEW_RESULT:`, or `VERIFY_RESULT:` markers are scope issues
  until reconstructed from git, docs, and evidence.

## Output

Start with:

```md
## Integration Action
Mode: RESULT_INTAKE | REVIEW_VERIFY | INTEGRATION_SYNC | BLOCKED_DECISION
Now: <what this integration terminal should do next>
Why: <one sentence grounded in repo evidence>
```

End accepted or blocked results with the `INTEGRATION_RESULT:` marker from
`../dev-flow/references/agent-contracts.md`.

```text
Use $integrate-lane-results to inspect worktree F:\SourceCodes\Rust\nako-worktrees\nako-storage-vfs-health.
Classify the result, run or assign review/verify, propose commit/merge/sync actions, and give the
next structured handoff block for the lane terminal only after the result is accepted.
```

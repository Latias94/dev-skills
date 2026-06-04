# Lane Map Contract

Use this contract whenever Loom splits a broad change without user-supplied parallelism.

## Required Discovery Summary

Before dispatch, state the evidence used:

- repo instructions read
- current branch/base and dirty state
- relevant ADRs/specs/workstream docs
- modules/packages inspected
- shared contracts or global files found
- verification commands or test surfaces available
- unknowns that require research lanes

## Template

```text
mode:
repo:
base_ref:
goal:
authority_order:
global_constraints:
verification_owner:
stop_conditions:
discovery_evidence:
- source:
  finding:
serial_first:
- reason:
  unlocks:
lanes:
- id:
  role: planner | researcher | architecture | worker | reviewer | merge_reviewer
  classification: parallel | serial-first | research-only | architecture-first | blocked
  status: planned | running | review | verified | blocked | closed
  target:
  depends_on:
  worktree:
  writable_files:
  forbidden_files:
  shared_contracts:
  expected_output:
  verification:
  reviewer:
```

## Split Rules

- Keep planners and reviewers read-only.
- Give each worker disjoint `writable_files`.
- Treat shared migrations, schemas, public contracts, generated APIs, global config, lockfiles, and repo instructions as serial until isolated.
- Prefer the smallest mergeable slice that can be verified independently.
- Put `AGENTS.md`, `CLAUDE.md`, `.trellis/`, settings, hooks, and install scripts in `forbidden_files` unless the goal targets them.
- Require fresh verification tied to the current head.
- If no safe parallel split exists, keep the lane serial and say so.

## Dispatch Shape

Use native Codex subagents or worktrees after the lane map is written. If native subagents are unavailable, output the lane map plus copyable prompts instead of pretending to dispatch.

Worker lanes must include:

- exact writable path globs
- exact forbidden files
- expected artifact or diff shape
- verification command
- stop condition for unexpected cross-lane edits

Reviewer lanes must include:

- read-only scope
- target diff/worktree/branch
- findings-first output
- explicit instruction to reject vague claims without file/line evidence

## Closeout Shape

```text
completed:
- lane:
  result:
  artifact:
  verification:

serial_or_blocked:
- lane_or_reason:
  evidence:
  next_action:

local_state:
- dirty_worktree:
- stale_branch:
- high_context_file_touched:
```

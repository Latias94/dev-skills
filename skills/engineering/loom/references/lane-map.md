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
success_metrics:
worktree_root:
commit_policy:
verification_owner:
observability:
stop_conditions:
discovery_evidence:
- source:
  finding:
serial_first:
- reason:
  unlocks:
lanes:
- id:
  role: planner | researcher | architecture | worker | reviewer | autonomy_watcher | merge_reviewer
  classification: parallel | serial-first | research-only | architecture-first | blocked
  status: planned | running | review | verified | blocked | closed
  target:
  depends_on:
  worktree:
  branch:
  commit_allowed:
  writable_files:
  forbidden_files:
  shared_contracts:
  expected_output:
  verification:
  reviewer:
  watch_scope:
```

## Split Rules

- Keep planners and reviewers read-only.
- Give each worker disjoint `writable_files`.
- Treat shared migrations, schemas, public contracts, generated APIs, global config, lockfiles, and repo instructions as serial until isolated.
- Prefer the smallest mergeable slice that can be verified independently.
- Put `AGENTS.md`, `CLAUDE.md`, `.trellis/`, settings, hooks, and install scripts in `forbidden_files` unless the goal targets them.
- Require fresh verification tied to the current head.
- If no safe parallel split exists, keep the lane serial and say so.

## Worktree Defaults

- Prefer existing worktrees that already match the target branch and base.
- For new worker lanes, recommend a sibling worktree root outside the main repo:

```text
../<repo-name>-worktrees/<goal-slug>/<lane-id>
```

- Use branches shaped like `codex/<goal-slug>/<lane-id>`.
- Keep read-only planner, researcher, and reviewer lanes in the main worktree unless isolation is useful.
- Never put worker worktrees under the main repo directory where they become untracked clutter.

## Commit Defaults

- When the user approved autonomous or bounded execution, worker lanes may commit their own scoped changes after verification passes.
- Use Conventional Commits and include only the lane's writable files.
- Do not push, merge, rebase shared branches, or amend existing commits unless the user explicitly asks.
- If repo instructions forbid self-commit, follow the repo instructions and report the conflict.
- Reviewers and researchers never commit.

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

Watcher lanes are required for autonomous or long-running execution and should include:

- the goal contract, run envelope, and current progress source to read
- execution drift checks: ignored errors, unverified claims, scope creep, stale metrics, or missing evidence
- direction drift checks: whether the work still serves the original goal and success metrics
- interrupt conditions and a concise status signal for the orchestrator

## Closeout Shape

```text
completed:
- lane:
  result:
  artifact:
  commit:
  verification:

merged:
- target:
  commit:

remaining:
- blocker_or_risk:
  next_action:

serial_or_blocked:
- lane_or_reason:
  evidence:
  next_action:

local_state:
- dirty_worktree:
- stale_worktree:
- remote_truth:
- stale_branch:
- high_context_file_touched:

feedback_loop:
- correction_or_missing_check:
  should_promote_to: skill | repo_instruction | test | checklist | none

next_recommended_decision:
```

## Failure Rules

- If a subagent returns vague output, ask for file/line evidence or rerun that lane with a stricter prompt.
- If a worker touches unassigned files, stop the lane and audit before continuing.
- If three attempts fail on the same class of problem, stop and challenge the hypothesis or split the lane differently.
- If hook, UI, or CI status looks stuck, verify process/log/check evidence before calling it stuck.
- If native subagents are unavailable, return the lane map and exact prompts for manual launch.
- Separate remote truth from local machine state in the final report.

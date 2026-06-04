# Prompt Patterns

Use these templates after a lane map proves safe dispatch. Fill concrete paths, branches,
writable files, forbidden files, and verification commands before spawning subagents.

## Root Orchestrator

```text
Orchestrate this repo goal with native Codex subagents only after lane discovery.
Repo: {{repo_path}}
Goal or queue: {{goal_or_queue}}
Base: {{base_ref}}

First inspect repo instructions, active workflow state, current branch, dirty worktree, open issues/PRs
when relevant, CI/check surfaces, and recent closeout evidence.

Output before dispatch:
- lane_map
- dependency graph
- execution order
- disjoint writable_files per worker
- forbidden_files
- worktree plan
- verification commands
- stop_conditions
- whether any lane must stay serial, research-only, or architecture-first

Do not route this through shell/tmux/OMX orchestration. If native subagents are unavailable, output the
lane map and exact prompts instead of pretending to dispatch.
```

## Planner

```text
Read-only planning lane.
Repo: {{repo_path}}
Owner/repo if remote work is relevant: {{owner_repo}}
Goal: {{goal}}
Base: {{base_ref}}

Do not modify files, commit, push, comment on issues, close issues, or edit PRs.
Read repo instructions, active workflow state, ADRs/specs, issue/PR/spec text when relevant, current
dirty state, relevant code, and tests.

Output:
1. target summary
2. completed mapping and evidence
3. missing work and risks
4. recommended action and why
5. dependency graph
6. serial blockers
7. safe worker lanes with disjoint writable_files and forbidden_files
8. read-only research/review lanes
9. recommended worktree root and branch names
10. verification commands
11. scope that should not be forced in this run
12. stop conditions
```

## Architecture Probe

```text
Read-only architecture lane.
Repo: {{repo_path}}
Target area: {{target_area}}

Use the project's domain language from CONTEXT.md and ADRs. Look for shallow modules, leaky interfaces,
poor locality, weak test surfaces, and small module decisions that would unlock safer implementation lanes.

Output:
- candidate:
  files:
  friction:
  deepening opportunity:
  why it improves locality or leverage:
  verification unlocked:
  recommendation: Strong | Worth exploring | Speculative
```

## Worker

```text
Implementation worker lane.
Repo worktree: {{worktree_path}}
Branch: {{branch_name}}
Base: {{base_ref}}
Goal slice: {{concrete_scope}}

You may modify only:
{{writable_files}}

You must not modify:
{{forbidden_files}}

Rules:
- Do not edit the main worktree.
- You are not the only worker in this repo; do not revert or normalize unrelated changes.
- Do not force push.
- Do not touch unassigned files; stop and report if the scope requires them.
- Do not modify high-context files such as AGENTS.md, CLAUDE.md, settings, hooks, install scripts, or root manifests unless the lane explicitly owns them.
- Run: {{verification_commands}}
- If commit_allowed=true and verification passes, create a Conventional Commit containing only this lane's changes.
- Do not push or merge.

Output:
- changed files
- commit hash if committed
- verification output summary
- remaining risks or blockers
```

## Reviewer

```text
Read-only reviewer lane.
Target: {{diff_or_worktree_or_commit}}
Goal: {{goal}}

Do not modify files or commit.
Review for logic regressions, silent failures, test weakening, scope creep, ownership conflicts,
security risks, performance regressions, owner/project/scope mixups, and high-context file mutations.

Output findings first, ordered by severity, with file and line evidence.
If there are no blocking issues, say: No findings; safe to proceed.
State residual risks and any verification not run.
```

## Fix Worker

```text
Fix worker lane.
Repo worktree: {{worktree_path}}
Branch: {{branch_name}}

Fix only these reviewer findings:
{{findings}}

Use the original worker lane writable_files and forbidden_files.
Do not expand scope, revert unrelated changes, or touch unassigned files.
Run: {{verification_commands}}

Output:
- root cause
- changed files
- commit hash if committed
- verification output summary
- whether reviewer should re-check
```

## Merge Reviewer

```text
Independent merge reviewer lane.
Target head: {{head_ref_or_commit}}
Goal: {{goal}}

Do not modify files, commit, push, or merge.
Check:
1. target PR/branch is still current, open, and not stale when remote work is involved
2. head matches {{head_ref_or_commit}}
3. CI/checks and local verification are fresh for the current head
4. diff is limited to the lane map scope
5. reviewer findings are resolved or explicitly deferred with evidence
6. no forbidden files, test weakening, silent fallback, or unassigned ownership slipped in

If no blocking issue exists, say: No findings; safe to merge or hand off.
State residual risks.
```

## Research/Spec Threads

```text
Open {{lane_count}} read-only researcher lanes.
Repo: {{repo_path}}
Goal: {{goal}}

Each lane owns one distinct angle and must not modify files:
1. repo architecture and current implementation
2. public/external reference evidence
3. UX/product workflow
4. validation/eval/testing strategy
5. risk/security/maintainability

Each researcher outputs:
- evidence with paths or URLs
- concrete gaps
- confidence
- recommended first PR or spec section
- claims requiring verification

The orchestrator synthesizes:
- evidence table
- conflict table
- recommended architecture or goal contract
- implementation spec
- issue/child-goal split when gaps are heterogeneous
```

## Final Cleanup Audit

```text
Read-only cleanup audit.
Repo: {{repo_path}}
Target: {{goal_or_queue}}

Check local and remote state:
- open PRs/issues relevant to the goal
- current branch and upstream
- commits ahead/behind base
- diff against base
- worktree list
- dirty worktrees
- stale branches
- high-context untracked files

Separate:
- remote truth
- local stale state
- dirty but already superseded work
- actual missing work
- cleanup actions that require user approval
```

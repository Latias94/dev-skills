# Prompt Patterns

Use these templates after a lane map proves safe dispatch. Fill concrete paths, branches,
writable files, forbidden files, and verification commands before spawning subagents.

## Planner

```text
Read-only planning lane.
Repo: {{repo_path}}
Goal: {{goal}}
Base: {{base_ref}}

Do not modify files or commit.
Read repo instructions, active workflow state, ADRs/specs, current dirty state, relevant code, and tests.

Output:
1. dependency graph
2. serial blockers
3. safe worker lanes with disjoint writable_files
4. read-only research/review lanes
5. recommended worktree root and branch names
6. verification commands
7. stop conditions
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
- Do not touch unassigned files; stop and report if the scope requires them.
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
security risks, and high-context file mutations.

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
Check that the final head matches the lane map, reviewer findings are resolved, verification is fresh,
and no forbidden files or unassigned ownership slipped in.

If no blocking issue exists, say: No findings; safe to merge or hand off.
State residual risks.
```

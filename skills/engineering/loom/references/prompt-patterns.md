# Prompt Patterns

Use these templates after a lane map proves safe dispatch. Fill concrete paths, branches,
writable files, forbidden files, and verification commands before spawning subagents.

## CE-First Router

```text
Route this repo goal through Compound Engineering when available.
Repo: {{repo_path}}
Goal: {{goal}}

First inspect repo instructions, dirty state, active planning memory, CE artifacts, branch/worktree
policy, forbidden files, and verification expectations.

If CE skills are installed:
- pick the CE entrypoint (`ce-brainstorm`, `ce-plan`, `ce-work`, `ce-debug`, `ce-code-review`, or `ce-compound`)
- pass the local constraints explicitly
- return to Loom only for safety closeout, fallback lanes, or fix routing that CE delegated back

If CE skills are unavailable or CE agents are missing:
- say exactly what is missing
- recommend the full CE plugin install
- produce a conservative fallback lane map only if the user wants to continue now
```

## Fallback Root Orchestrator

```text
Orchestrate this repo goal with native Codex subagents only after CE is unavailable or unsuitable and lane discovery proves it is safe.
Repo: {{repo_path}}
Goal or queue: {{goal_or_queue}}
Base: {{base_ref}}

First inspect repo instructions, active workflow state, current branch, dirty worktree, open issues/PRs
when relevant, CI/check surfaces, and recent closeout evidence.

Output before dispatch:
- lane_map
- dependency graph
- execution order
- external_workflow policy, including whether Compound Engineering is installed and which steps it owns
- disjoint writable_files per worker
- forbidden_files
- worktree plan
- verification commands
- success metrics
- status/observability signals
- autonomy watch plan for long-running work
- stop_conditions
- whether any lane must stay serial, research-only, or architecture-first

Do not route this through shell/tmux/OMX orchestration. If native subagents are unavailable, output the
lane map and exact prompts instead of pretending to dispatch.
```

## Compound Engineering Bridge

Use these as the default path when CE skills are installed. If they are not installed, recommend CE
installation before using fallback Loom-native lanes.

### Requirements / Brainstorm

```text
Invoke $ce-brainstorm for this goal before Loom lane discovery:
{{goal}}

Keep output portable and repo-relative. After it writes the requirements doc, return to Loom discovery
with the requirements doc as authority.
```

### Plan

```text
Invoke $ce-plan for this goal or requirements doc:
{{goal_or_requirements_path}}

After the plan is written under docs/plans/, return to Loom. Treat the plan as a decision artifact;
do not duplicate it into the lane map. The lane map should reference the plan path and own only
parallelism, worktree policy, review gates, and closeout.
```

### Work

```text
Invoke $ce-work on this plan:
{{plan_path}}

Loom remains responsible for repo-level safety: user dirty state, worktree policy, independent review
requirements, and final closeout. If ce-work cannot run because CE agents are missing, continue with
Loom-native worker lanes from the lane map.
```

### Review

```text
Invoke $ce-code-review mode:agent {{base_arg}} {{plan_arg}}

Use report-only mode. Parse actionable findings, batch fixes only inside the original writable_files,
run fresh verification, and re-check unresolved findings before closeout.
```

### Knowledge Capture

```text
Invoke $ce-compound mode:headless {{context_hint}}

Use only after the fix or feature is verified. If unavailable, record the learning in the closeout's
feedback_loop and recommend documenting it.
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

## Autonomy Watcher

```text
Read-only autonomy watcher lane.
Goal contract: {{goal_contract}}
Run envelope: {{run_envelope}}
Primary progress source: {{progress_source}}
Target worktree or session evidence: {{target}}

Do not modify files, commit, push, comment remotely, or change task state.

Check execution drift frequently:
- ignored errors or failed commands
- unverified success claims
- scope creep beyond writable_files or goal contract
- stale metrics, stale branch, or missing evidence
- repeated failed attempts without a changed plan

Check direction drift occasionally:
- whether current work still serves the original goal
- whether success metrics and done_when still match the user's intent
- whether a research-only or architecture-first pause is now safer than continuing

Output:
- status: on_track | needs_correction | stop_and_replan
- findings first, with file/session/progress evidence
- exact correction to send to the primary lane
- checks that must run before the next commit or closeout
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

## Documentation Onboarding Threads

```text
Open three read-only onboarding lanes for an existing repo with unclear or AI-generated docs.
Repo: {{repo_path}}
Goal: understand the project before changing docs or code.

Lane 1: Doc Cartographer
- Read README, AGENTS/CLAUDE instructions, CONTEXT, docs, ADRs, roadmap, workstreams, .loom, .planning, and legacy workflow state.
- Classify each source as durable authority, active work, evidence archive, stale, or unknown.
- Output authority order, conflicts, and the smallest docs or workflow files that should exist.

Lane 2: Code Reality Checker
- Inspect manifests, module roots, key entrypoints, and tests, then follow imports, call sites, and
  verification evidence until important documentation claims are defensible.
- Check whether important documentation claims match the current code.
- Output confirmed claims, contradicted claims, and areas needing deeper inspection.

Lane 3: Verification Mapper
- Find test, lint, build, CI, benchmark, fixture, and smoke-test surfaces.
- Identify fast checks for likely first goals and missing verification surfaces.
- Output commands, confidence, and prerequisites.

The orchestrator synthesizes:
- whether `.loom` should be initialized; default to `.loom/state.local.json` and `.loom/goals/`
  when no existing workflow memory already owns active state
- whether docs should be left alone, reconciled, or minimally created
- candidate first goal
- whether Loom should proceed to lane discovery or stay architecture-first
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

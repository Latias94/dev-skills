---
name: loom
description: Parallel lane discovery and orchestration for broad codebase changes. Use when the user wants Codex to inspect the repo, discover safe parallel work itself, split a large task into independent lanes, spawn subagents or worktrees, identify serial blockers, deepen architecture before feature work when module boundaries are too coupled, or coordinate review-gated implementation.
---

# Loom

Use Loom to turn a broad repo goal into an evidence-backed lane map before implementation.

## Core Rule

Do not ask the user to pre-partition the work. Discover the split from code, docs, ADRs, tests, and current git state.

Loom is the orchestration layer. Durable decisions belong in ADRs/specs/workstream docs. Native subagents and worktrees should be coordinated directly from the lane map when available.

## Workflow

1. Intake
   - Capture the goal, done-when, constraints, and whether edits are allowed.
   - If the user only gives an outcome, proceed; do not require a manual lane registry.
   - For longer or low-interaction execution, require an approved durable task/plan, run envelope, and explicit stop conditions.
2. Discover
   - Read repo instructions, relevant ADRs, current docs, open workstream/task evidence, and dirty state.
   - Inspect dependency direction, shared contracts, writable files, test surfaces, and risky global state.
   - Explore as deeply as needed to make lane ownership defensible; turn independent unknowns into research lanes.
   - Launch read-only research lanes when architecture, risk, or verification shape is unclear.
3. Synthesize lanes
   - Build a lane map from evidence, not intuition.
   - Mark each candidate as parallel, serial-first, research-only, architecture-first, or blocked.
   - Prefer lanes with disjoint writable files, independent verification, and explicit stop conditions.
   - If safe lanes require better module boundaries first, open an architecture lane with `improve-codebase-architecture`.
4. Dispatch
   - Use native Codex subagents or worktrees for planner, worker, reviewer, and merge-reviewer lanes when available.
   - If a `threads` skill is installed, it may provide prompt shapes, but Loom must remain self-sufficient from the lane map.
   - Read `references/prompt-patterns.md` before spawning subagents or writing manual prompt packs.
   - Let subagents inherit the current model and reasoning strength unless the user requests otherwise.
   - Keep planners/researchers/reviewers read-only; give workers disjoint writable paths.
   - For low-interaction work, prefer one implementation lane plus read-only research/check lanes unless the user approved multiple disjoint writers.
   - Put high-context repo files in `forbidden_files` unless the request explicitly targets them.
5. Gate
   - Require one independent review per implementation lane.
   - Require fresh verification tied to the current head before merge or handoff.
   - Do not merge from worker output alone.
6. Close out
   - Report completed lanes, artifacts, verification, remaining blockers, and local dirty state.
   - Capture lasting decisions in ADRs/specs/workstream docs if the repo already uses them.

## Example

```text
User: Make the Rust ingestion pipeline faster and easier to extend.
Loom: reads repo instructions, ADRs, Cargo workspace layout, recent diffs, ingestion tests, and module ownership; finds that parser cleanup and metric export are parallel, but storage schema changes are serial-first; dispatches two worker lanes with disjoint writable files plus one read-only reviewer lane per worker.
```

## References

- Read `references/discovery-rules.md` before deciding whether work can run in parallel.
- Read `references/lane-map.md` before writing the lane map or dispatching workers.
- Read `references/prompt-patterns.md` before spawning subagents, assigning worktrees, or allowing worker commits.
- Use native Codex subagents/worktrees for planner, worker, reviewer, and merge-reviewer lanes when the lane map proves safe dispatch.

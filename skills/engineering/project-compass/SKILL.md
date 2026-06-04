---
name: project-compass
description: Long-term project direction and file-based planning memory for Codex. Use when the user wants to initialize a lightweight `.loom` workflow, brainstorm or clarify a broad product/architecture goal, define a project north star, maintain roadmap and project memory files, resume long-running development, decide the next executable goal, or hand a clarified goal to Loom for parallel implementation.
---

# Project Compass

Use Project Compass before execution when the work is bigger than one coding task and the project needs durable memory.

## Core Rule

Do not keep project direction only in chat. Capture durable decisions, goals, boundaries, and progress in lightweight repo files, then hand concrete goals to `loom`.

Project Compass is the direction layer. `loom` is the execution layer. ADRs/specs/roadmaps/workstream docs are the memory layer.

If existing memory shows unresolved active work, reconcile or close it out before selecting a competing next goal.

Do not require Trellis, planning-with-files, or any external workflow runtime. Adapt existing repo memory when present; otherwise use the default `.loom/` contract.

## Workflow

1. Orient
   - Read repo instructions and existing planning memory before proposing new files.
   - Prefer existing structures: `.loom/`, `.planning/`, `docs/adr/`, `CONTEXT.md`, roadmap docs, workstream docs, or issue tracker links.
   - If `.loom/` is missing and the user is onboarding, resuming, or asking for long-running planning, ask whether to initialize the lightweight `.loom` state and gitignore policy.
   - Keep initialization minimal: local active pointer, goal directory when needed, and gitignore entries for runtime noise.
   - If legacy `.trellis/` structures exist, read them as existing memory; do not create or require them.
   - If no memory structure exists, use `references/planning-files.md`.
2. Brainstorm
   - Clarify the north star, target users, non-goals, capability map, constraints, and quality bar.
   - Ask only questions that change product direction, architecture boundaries, or next-goal ordering.
3. Shape durable memory
   - Update or create focused planning files instead of one monolithic plan.
   - Keep long-term facts separate from short-lived execution notes.
   - For active multi-session goals, use scoped planning files under `.loom/goals/<slug>/`.
   - Record architecture decisions as ADRs when they constrain future work.
4. Choose the next goal
   - Convert the roadmap into one concrete goal with done-when, dependencies, risks, and verification.
   - If active work is stale, incomplete, or contradictory, produce a reconciliation/closeout goal first.
   - Mark whether it is ready for `loom`, needs `improve-codebase-architecture`, or should become issues with `to-issues`.
   - If work should continue with limited user input, define a run envelope with subagent, worktree, and commit policy before approving execution.
5. Hand off execution
   - Use `loom` when the goal is ready for lane discovery, parallel implementation, review gates, and closeout.
   - Let `loom` decide whether native threads/subagents are safe; do not call them directly from Project Compass.
6. Close the loop
   - After implementation, update roadmap status, ADRs, capability map, and workstream closeout as needed.
   - Run the 5-question reboot check before stopping or resuming a long-running goal.
   - Recommend a refactor pulse when feature work has created coupling, duplicated concepts, weak tests, or unclear module boundaries.

## Example

```text
User: Nako should become a self-hosted multimedia server like Jellyfin, but more modular and extensible.
Project Compass: writes a north star, capability map, module-boundary sketch, phased roadmap, and the next executable goal. The next goal is then handed to Loom for lane discovery and review-gated execution.
```

## References

- Read `references/planning-files.md` before creating or updating project memory files.
- Read `references/goal-loop.md` when turning a long-term direction into repeated development cycles.
- Read `references/run-envelope.md` when execution needs explicit autonomy, scope, stop, and evidence boundaries.
- Read `references/upstream-skill-policy.md` before vendoring external skills or making them workflow requirements.
- Use `loom` for execution. Optional upstream skills such as `improve-codebase-architecture`, `to-issues`, and `codex-retrospective` may help when installed or vendored, but Project Compass must remain usable without them.

# Subagent Delegation

Use this when the planner can use Codex subagents in addition to human-opened terminals and
worktrees.

Subagents are optional accelerators, not durable state owners. The user does not need to name
subagents explicitly: if the invoked workflow is architecture review, code-aware lane planning, or
multi-agent coordination, explorer subagents can be an internal technique. Use them only when a
scoped side task can run without blocking the planner's immediate next step.

## Good Uses

- Explorer subagents for independent code questions during code-aware planning or architecture
  review:
  - current call flow and ownership,
  - test seams and validation gates,
  - shared-scope conflicts,
  - docs/code drift in one lane.
- Reviewer sidecars for read-only diff review while the planner checks docs or runs verification.
- Worker subagents only when the user asked for delegated implementation and the write scopes are
  disjoint enough for the planner to review and integrate.

For long-lived architecture-lane work, prefer stable terminals and worktrees. Subagents should not
replace the planner, own lane state, or choose global sequencing.

## Prompt Shape

Give each subagent:

- one concrete question or task,
- repo/worktree path,
- read or write scope,
- relevant workstream/ADR/context paths,
- expected output format,
- instruction not to revert or overwrite others' changes.

For explorer tasks, request files inspected, evidence, uncertainty, and planner implications. Treat
the result as input evidence; the planner still decides the plan.

## Stop Rules

Do not use subagents for side effects that require user approval unless that approval already exists:
worktree creation/deletion, branch operations, shared-scope edits, commits, merges, pushes, or
related-repo changes. If no subagent tool is available, continue with local inspection.

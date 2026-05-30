# Development Stage Map

Use this when `$dev-flow` must decide the next project-development phase or make the user's next
action obvious.

## Stage Routing

| Stage | Signals | Route | Agent should decide | User should see |
| --- | --- | --- | --- | --- |
| Intake | User intent is broad or repo state is unknown | `audit-project-scale` or `grill-with-docs` | Whether scale or requirements are the first risk | Current phase, first read-only step, approval needed |
| Setup | Missing `AGENTS.md`, `CONTEXT.md`, or workstream docs | `setup-rust-workstreams` | Minimal workflow substrate for this repo size | Files to create/update and why |
| Requirements | Goal is fuzzy, risky, or domain language is unstable | `grill-with-docs` | Which terms/constraints must be settled before planning | Decisions captured and remaining open questions |
| Architecture direction | User picked a capability area or refactor theme | `plan-architecture-lane` | Planning depth: light, code-aware, or architecture review | Evidence read, whether explorers/review are needed |
| Architecture review | Seams or docs/code alignment are unclear | `improve-codebase-architecture` | Scoped review area and candidate deepening opportunities | Report path and which candidate needs user choice |
| Durable planning | Work spans multiple slices or sessions | `open-workstream` | Reuse or create workstream; task ledger shape | Workstream path, task IDs, gates, context manifest |
| Parallel planning | Multiple terminals or worktrees are active | `coordinate-workstream` | Lane bundles, worktrees, scopes, conflicts, prompts | Planner action, terminal prompts, approvals |
| Lane execution | One terminal owns a capability area | `run-architecture-lane` | Current approved bundle and stop conditions | Same-lane progress report to return to planner |
| Task execution | One task ID has scope and validation | `run-workstream-task` | Whether to route to `tdd`, `diagnose`, or `zoom-out` | DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_CONTEXT |
| Bug or flake | Failure signal dominates | `diagnose` | Repro loop and hypotheses before fixing | Repro evidence, fix scope, regression result |
| Refactor execution | Architecture candidate is confirmed | `fearless-refactor` | Scope, deletion plan, gates, and workstream fit | Refactor lane plan and validation |
| Review | Worker/lane reports completion | `review-workstream` | Contract and code-quality findings | Blocking findings first, then residual risk |
| Verification | Completion claim needs proof | `verify-rust-workstream` | Fresh commands that prove the exact claim | Command evidence and skipped-gate rationale |
| Integration | Reviewed and verified branch can land | `coordinate-workstream` | Commit/merge/sync order and side-effect approvals | Exact proposed side effects and next bundle |
| Closeout | Workstream gates are satisfied | `close-workstream` | Close, split follow-on, or keep active | Final status, evidence, follow-on path |
| Resume/recovery | Context changed, session crashed, or user asks continue | `resume-workstream`, `handoff`, or `codex-session-recovery` | Authoritative state source | Safe continuation plan |
| External tracker | Plan should become PRD/issues | `to-prd`, then `to-issues` | Whether tracker artifacts add value | Artifact location and next local workflow step |

## Response Contract

When the user does not know the next step, say:

1. Current phase and why.
2. Recommended route and why alternatives are not first.
3. Read-only actions the agent will take immediately.
4. Side effects that need approval.
5. Expected artifact path or terminal prompt.
6. Stop condition and next likely phase.

Prefer concrete recommendations over asking the user to choose from internal skills. Ask only for
product decisions, irreversible side effects, or missing context that cannot be inferred safely.

## Goal Readiness

When scope, docs, validation, owner, and stop conditions are clear enough for longer autonomous work,
recommend a bounded Codex goal and ask whether to set it. Good targets are one `TODO.md` task, one
planner-approved lane goal bundle, one diagnosis loop with a repro command, or one refactor
milestone with gates.

Do not recommend a goal for a whole architecture lane, an entire workstream, vague discovery, or a
task whose acceptance gates are still unknown. Goal text should be copyable, for example:

```text
Set the current Codex goal to complete planner-approved lane bundle <BUNDLE-ID>.
```

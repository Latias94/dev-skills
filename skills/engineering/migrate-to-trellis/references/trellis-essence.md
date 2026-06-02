# Trellis Essence

Trellis is not primarily a documentation layout. It is a workflow runtime that keeps the main
agent, subagents, task state, and durable project knowledge aligned.

## Core Model

| Concept | What it owns | What it should not own |
| --- | --- | --- |
| `.trellis/workflow.md` | Phase state, routing rules, per-turn breadcrumbs | Project-specific implementation details |
| `.trellis/tasks/<task>/` | One unit of work: PRD, research, context manifests, task status | Long-term architecture canon |
| `.trellis/spec/` | Durable executable project knowledge and quality checks | One-off task requirements |
| `research/` | Persisted investigation for a task | Chat-only summaries |
| `implement.jsonl` | Spec/research context for implement agents | Source-code file lists |
| `check.jsonl` | Spec/research context for check agents | Test output dumps or old task ledgers |
| workspace journal | Session memory | Active task queue |

## Workflow Loop

1. No active task: direct answer for small Q&A, otherwise create a task.
2. Planning: brainstorm, inspect/research before asking, write/iterate `prd.md`.
3. Context curation: fill `implement.jsonl` and `check.jsonl` with spec/research files.
4. Execution: main session dispatches implement agent, not direct code edits by default.
5. Verification: check agent reviews/fixes against specs and runs checks.
6. Finish: update specs with durable lessons, commit, archive task, record session.

## What Makes Trellis Work

- The per-turn `<workflow-state>` breadcrumb is short and authoritative.
- `workflow.md` is the single editable source for phase guidance.
- Task directories carry all transient execution context.
- Spec files carry only reusable knowledge.
- Subagents are role-specific and isolated.
- Research must persist to files; chat summaries are not enough.
- `implement.jsonl` and `check.jsonl` route context; they are not a source-code manifest.

## Migration Implication

Legacy workstream systems usually mix four concerns:

1. task assignment,
2. architecture knowledge,
3. validation evidence,
4. historical session handoff.

Trellis splits them. During migration:

- active assignment becomes Trellis tasks,
- architecture knowledge becomes ADRs/specs/guides,
- validation rules become spec quality checks or check context,
- historical handoffs become task research only when still useful; otherwise they are retired and
  recoverable from git history.

Do not recreate the old workstream queue inside Trellis.

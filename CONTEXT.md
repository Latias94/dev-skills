# Dev Skills Context

## Language

**Workstream**
: A durable engineering lane for one product or architecture goal. It owns design, task ledger,
milestones, evidence, gates, and closeout. It is broader than one task and narrower than the whole
project roadmap.

**Task ledger**
: The canonical list of executable slices inside a workstream. It records status, owner, file scope,
dependencies, and validation. It is usually `docs/workstreams/<slug>/TODO.md`.

**Session journal**
: A short-lived execution memory for agent handoff and resume. It records what happened in a
session, but it is not a source of truth for architecture or product decisions.

**Evidence gate**
: A command, test, demo, audit, or artifact that proves a slice or milestone is complete.

**Planner**
: The agent or human responsible for turning a clarified requirement into a workstream and task
ledger.

**Worker**
: The agent responsible for one bounded task from the ledger. Workers may refine local steps but do
not rewrite the global plan without escalation.

## Source Of Truth Order

1. ADRs and accepted architecture contracts
2. Workstream design, milestones, and gates
3. Task ledger
4. Session journal and handoff notes
5. Chat history

## Avoid

- Calling session journals "memory" without saying where the files live.
- Creating a new workstream for every task.
- Letting multiple agents independently rewrite task boundaries.

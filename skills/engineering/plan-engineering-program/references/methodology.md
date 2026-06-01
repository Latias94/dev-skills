# Program Methodology

Use this to explain why the workflow exists and to guide planning choices.

## Mission

Reduce repeated prompting by encoding intent in durable engineering artifacts. The workflow should
let the user chat naturally with specialized lane terminals while one upper architecture terminal
maintains macro control, integration order, and architecture memory.

## Principles

- **Intent compression**: prefer named lane docs, campaigns, ADRs, and validation gates over long
  chat prompts. A short prompt should point to durable context.
- **Bounded autonomy**: give lane terminals enough authority to deepen their sub-architecture, but
  stop them before shared contracts, ADRs, schemas, merges, or failed gates.
- **Capability ownership**: model large systems as architecture lanes similar to bounded contexts or
  stream-aligned teams. Each lane owns a coherent capability, not a random task list.
- **Vertical value slices**: plan work so every campaign creates observable capability or stronger
  architectural leverage, not only horizontal scaffolding.
- **Critical-path realism**: do not fake parallelism. Use serial lane campaigns when the work is a
  dependency chain or shares hot files.
- **Refactor before entropy compounds**: use code-aware planning and architecture review before the
  lane backlog becomes a pile of tactical TODOs.
- **Evidence over claims**: worker/lane reports are inputs; review and fresh verification decide
  acceptance.
- **User attention is scarce**: spend more agent time and tokens on reading code, docs, and gates so
  user prompts stay high-level and decision-focused.
- **First-principles simplification**: delete weak scope, challenge copied requirements, and make
  the smallest product promise that proves the next architecture step.
- **Manufacturing-line thinking**: optimize the whole loop from planning to integration, not local
  agent busyness. Track handoffs, failed gates, merge conflicts, and user interruptions as waste.
- **No named-person cargo cults**: encode operating constraints and measurable behavior instead of
  invoking executive personas in skill instructions.
- **Behavioral verification**: passing skill format checks is not enough. Re-run representative
  prompts or session traces when the workflow changes.

## Borrowed Methods

- **Domain-Driven Design**: use `CONTEXT.md`, ADRs, and lane vocabulary as the shared language.
- **Team Topologies**: treat lanes like stream-aligned capability teams; shared crates are platform
  or collaboration seams.
- **Shape Up**: use medium-sized appetite/campaigns instead of tiny prompt churn or unbounded goals.
- **Mikado Method**: for refactors, map enabling moves and dependencies before touching shared
  contracts.
- **Theory of Constraints**: optimize the bottleneck lane and critical path, not terminal count.
- **XP/TDD**: keep fast feedback loops and behavior-level tests at the campaign/task boundary.
- **Continuous Delivery**: integrate reviewed and verified slices frequently enough to avoid branch
  drift.
- **Superpowers/GSD/Trellis**: front-load design, keep state in files, run continuously inside
  approved plans, and use review gates before accepting output.

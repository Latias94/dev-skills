# Matt Skill Leverage

Use upstream skills as tools inside the program workflow. Do not copy their bodies.

- `grill-with-docs`: use when requirements, domain terms, non-goals, or ADR candidates are unclear.
- `zoom-out`: use before planning in unfamiliar code or when a lane's call flow is not understood.
- `improve-codebase-architecture`: use proactively when the lane queue is thin, docs/code drift is
  suspected, future depth is unclear, or shared seams look wrong.
- `prototype`: use before ADRs when two designs are plausible and a throwaway experiment can decide.
- `tdd` / `diagnose`: use after a task is assigned and the work is executable.
- `handoff`: use when stopping, switching terminals, or preserving a lane/campaign result.
- `to-prd` / `to-issues` / `triage`: use only when the repo uses an external issue workflow.

Bias toward read-only investigation before asking the user. Stop and ask only after the best
recommendation is formed and the remaining decision is genuinely product, contract, or side-effect
approval.

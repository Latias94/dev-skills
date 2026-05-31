# Architecture Lanes

Use this registry only when the project is large enough for one terminal or worktree to own a
capability area across multiple workstreams.

## Lane Registry

| Lane | Architecture refs | Owned scopes | Shared scopes | Active workstream | Queue | Current goal bundle | Worktree / branch | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| storage | `docs/architecture/STORAGE.md` | `crates/<project>-storage` | `crates/<project>-core`, `crates/<project>-db` | _none_ | _none_ | _none_ | _none_ | idle |

## Rules

- Prefer a stable terminal/worktree with short-lived branches per workstream.
- Owned scopes can move inside the lane; shared scopes require planner coordination.
- Close and verify the active workstream before starting the next queued workstream.
- A goal bundle is one planner-approved unit of lane work: task IDs, context manifest, validation,
  and stop conditions. Do not make the whole lane one unbounded goal.
- If a lane should keep maturing, track target maturity, capability gaps, deferred workstreams,
  validation ladder, and next bundles in a lane roadmap or capability map.
- If requirements and gates are clear, a planner may define an ordered lane campaign so one terminal
  can auto-advance through multiple approved bundles until a stop condition appears.
- Do not use architecture lanes for small projects or one-off tasks.

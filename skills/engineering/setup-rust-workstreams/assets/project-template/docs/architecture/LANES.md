# Architecture Lanes

Use this registry only when the project is large enough for one terminal or worktree to own a
capability area across multiple workstreams.

## Lane Registry

| Lane | Architecture refs | Owned scopes | Shared scopes | Active workstream | Queue | Worktree / branch | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| storage | `docs/architecture/STORAGE.md` | `crates/<project>-storage` | `crates/<project>-core`, `crates/<project>-db` | _none_ | _none_ | _none_ | idle |

## Rules

- Prefer a stable terminal/worktree with short-lived branches per workstream.
- Owned scopes can move inside the lane; shared scopes require planner coordination.
- Close and verify the active workstream before starting the next queued workstream.
- Do not use architecture lanes for small projects or one-off tasks.

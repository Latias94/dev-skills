# Planner Runtime State

Use runtime state when a planner coordinates multiple worktrees, branches, or related repositories.
Keep it local-only unless the project explicitly wants to publish machine-independent paths.

Recommended local fields:

```json
{
  "updated": "YYYY-MM-DD",
  "baseline": {
    "repo": "<primary repo>",
    "branch": "main",
    "head": "<short sha>",
    "status": "clean|dirty",
    "ahead_behind": "<git status summary>"
  },
  "terminals": [
    {
      "role": "planner|lane|worker|reviewer|docs",
      "lane_slug": "<lane>",
      "repo_path": "<local path>",
      "branch": "<branch>",
      "head": "<short sha>",
      "workstream": "docs/workstreams/<slug>",
      "task": "<TASK-ID>",
      "status": "ready|running|blocked|done",
      "shared_scopes": ["<paths or contracts>"],
      "validation": ["<commands>"]
    }
  ],
  "related_repos": [
    {
      "name": "<repo>",
      "path": "<local path>",
      "branch": "<branch>",
      "head": "<short sha>",
      "status": "clean|dirty|diverged"
    }
  ]
}
```

Storage guidance:

- Prefer `.codex/planner-state.local.json` or `docs/local/PLANNER_STATE.md`.
- Add the local file to `.git/info/exclude` or `.gitignore` before writing secrets or absolute
  machine paths.
- Commit only machine-independent examples or lane names, not personal paths.
- Refresh state before assigning work and after every branch sync, task completion, or handoff.

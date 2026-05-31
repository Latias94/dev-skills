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
      "id": "planner-main",
      "role": "planner|lane|worker|reviewer|docs",
      "lane_slug": "<lane>",
      "repo_path": "<local path>",
      "branch": "<branch>",
      "head": "<short sha>",
      "workstream": "docs/workstreams/<slug>",
      "task": "<TASK-ID>",
      "goal": "<planner-approved task, lane bundle, or lane campaign>",
      "goal_scope": "task|lane_bundle|lane_campaign|review|docs",
      "status": "ready|running|blocked|done|needs-planner",
      "shared_scopes": ["<paths or contracts>"],
      "validation": ["<commands>"],
      "context_manifest": "docs/workstreams/<slug>/CONTEXT.jsonl",
      "session_refs": [
        {
          "platform": "codex",
          "session_id": "<optional session id>",
          "notes": "Pointer for recovery only; docs remain authoritative."
        }
      ],
      "last_report": {
        "at": "YYYY-MM-DDTHH:MM:SSZ",
        "status": "DONE|DONE_WITH_CONCERNS|BLOCKED|NEEDS_CONTEXT",
        "summary": "<short terminal report>"
      }
    }
  ],
  "lane_goal_bundles": [
    {
      "id": "<lane>-YYYYMMDD-01",
      "lane_slug": "<lane>",
      "workstream": "docs/workstreams/<slug>",
      "tasks": ["<TASK-ID>", "<TASK-ID>"],
      "scope": ["<owned paths>"],
      "shared_scopes": ["<paths requiring planner approval>"],
      "validation": ["<commands>"],
      "stop_conditions": ["<when the lane terminal must stop>"],
      "approved_by_user": false
    }
  ],
  "lane_campaigns": [
    {
      "id": "<lane>-YYYYMMDD-campaign-01",
      "lane_slug": "<lane>",
      "worktree": "<local path>",
      "ordered_bundles": ["<lane>-YYYYMMDD-01", "<lane>-YYYYMMDD-02"],
      "auto_advance_rule": "continue only when each listed gate passes",
      "checkpoints": ["after each bundle"],
      "stop_conditions": ["failed gates", "shared scopes", "ADR/schema/contract changes"],
      "approved_side_effects": ["<optional task-boundary commits>"],
      "approved_by_user": false
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
- Use `session_refs` as recovery pointers only. Do not make planner decisions from raw chat history
  unless project docs or terminal reports are missing.
- When coordinating an active worktree, use `scripts/session_tail_for_worktree.py <worktree>` to
  combine the latest visible assistant message with repo evidence before asking the user to paste
  chat manually.
- Use `lane_goal_bundles` or `lane_campaigns` for long-running lane terminals. A bundle should be
  larger than one tiny edit; a campaign may contain several approved bundles with auto-advance gates.
  Both need clear stop conditions.

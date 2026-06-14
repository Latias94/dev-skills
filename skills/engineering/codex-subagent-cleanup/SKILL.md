---
name: codex-subagent-cleanup
description: Find and close stale Codex subagents by scanning Codex session JSONL logs for spawned agents that were completed but not closed. Use when the user says Codex subagents were not closed, hits a subagent/thread/concurrency limit, asks to clean up stale agents, or needs a safe way to identify inactive Codex subagent sessions before calling close_agent.
---

# Codex Subagent Cleanup

Use this skill to recover subagent capacity without guessing from memory. Close only Codex subagent
handles with `close_agent`; do not kill Codex OS processes from this skill.

## Workflow

1. Scan first; do not close anything from memory. By default, only completed subagents that have
   been idle for at least 30 minutes are recommended for closure.

```powershell
python "$env:CODEX_HOME\skills\codex-subagent-cleanup\scripts\codex_subagent_cleanup.py"
```

When `CODEX_HOME` is unset:

```powershell
python "$HOME\.codex\skills\codex-subagent-cleanup\scripts\codex_subagent_cleanup.py"
```

2. Close session-level candidates with `multi_agent_v1.close_agent` when the tool is available.
   The script reports ids whose session logs show `spawn_agent` succeeded, the subagent completed,
   stayed idle for the configured threshold, and no matching `close_agent` or shutdown notification
   was recorded. The default closure threshold is 30 minutes.
   If `close_agent` returns `not found`, treat that historical agent as no longer present in the
   current runtime registry.

## Safety Rules

- Treat the default output as a dry run.
- Prefer `close_agent` over OS process termination whenever an agent id is known.
- Do not close subagents that are still running or have no completed notification unless the user
  explicitly accepts the risk.
- Treat the 30-minute idle threshold as the default recommendation, not a hard rule.
- If the candidate list is ambiguous, show it to the user instead of guessing.

## Useful Options

```powershell
python codex_subagent_cleanup.py --mode sessions --days 2 --max-files 80
python codex_subagent_cleanup.py --mode sessions --min-completed-idle-minutes 60
python codex_subagent_cleanup.py --json
python codex_subagent_cleanup.py --session "C:\Users\you\.codex\sessions\...\rollout-....jsonl"
```

## Example

```text
Use $codex-subagent-cleanup to find completed Codex subagents that were not closed. Run the dry
run first, then close only the listed completed-and-idle agent ids with close_agent.
```

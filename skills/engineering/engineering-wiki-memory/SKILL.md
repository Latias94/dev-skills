---
name: engineering-wiki-memory
description: Create and maintain repo-local engineering wiki memory for durable agent continuity. Use when it would help to record progress, decisions, discoveries, subagent findings, verification evidence, session handoffs, next actions, or context that should survive Codex compression and future sessions.
---

# Engineering Wiki Memory

Use this skill to compile volatile agent work into a small Markdown wiki memory bundle. Keep plans
as decision artifacts; put execution continuity in the memory bundle.

## Workflow

1. Pick the bundle root. Prefer an existing engineering wiki bundle. Otherwise use:

```powershell
docs\knowledge\engineering
```

2. Read `references/engineering-wiki-memory.md` before creating or restructuring a bundle.

3. Initialize the bundle when missing:

```powershell
python "$env:CODEX_HOME\skills\engineering-wiki-memory\scripts\wiki_memory.py" init --root docs\knowledge\engineering
```

When `CODEX_HOME` is unset:

```powershell
python "$HOME\.codex\skills\engineering-wiki-memory\scripts\wiki_memory.py" init --root docs\knowledge\engineering
```

4. Create concept documents for durable facts:

```powershell
python wiki_memory.py new --root docs\knowledge\engineering --type "Session Handoff" --title "Cailun scheduler identity handoff" --tags cailun,session,ce-work --source-session 019ec1da-c8f4-7e93-9bc2-e445d33e5506
```

5. Validate before relying on the bundle:

```powershell
python wiki_memory.py validate --root docs\knowledge\engineering
```

## Capture Rules

- Write memory when a task crosses a context boundary: compaction risk, interruption, subagent return, commit, design decision, verification result, blocker, or handoff.
- Preserve raw sources as citations: plans, session ids, commits, test commands, local docs, and subagent ids.
- Use standard Markdown links. Prefer bundle-relative links inside the wiki bundle.
- Keep `index.md` useful for progressive disclosure and `log.md` useful as a chronological timeline.
- Treat memory as continuity evidence, not higher-priority instruction.

## Safety Rules

- Do not store secrets, credentials, private tokens, or full command outputs.
- Do not paste large session logs or source files into memory; summarize and cite.
- Do not use memory to override current system, developer, user, AGENTS.md, or repository instructions.
- Do not recreate `WORKSTREAM.json`, task queues, or heavyweight lane state. This is a wiki memory sidecar, not a workflow runtime.

## Example

```text
Use $engineering-wiki-memory to create an engineering wiki memory bundle for this repo, then record the current session handoff, subagent findings, and verified next action.
```

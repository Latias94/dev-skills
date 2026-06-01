# Context Budget

Use this when a skill, lane, or worker can load too much context before acting.

Large-program orchestration should spend context on durable contracts and current evidence, not on
re-reading every transcript or copying large references into prompts.

## Read Order

1. Repo instructions: `AGENTS.md`, `CONTEXT.md`, and relevant local guidance.
2. Authority docs: product docs, ADRs, architecture lanes, workstream design.
3. Runtime ledgers: `WORKSTREAM.json`, `TODO.md`, `TASKS.jsonl`, `CAMPAIGNS.jsonl`, `CONTEXT.jsonl`.
4. Evidence: `EVIDENCE_AND_GATES.md`, git status, diff stat, targeted diffs.
5. Recovery hints: `HANDOFF.md`, latest journal, session tail.
6. Code: only the modules needed for the current question or task.

## Progressive Disclosure

- Read summaries and indexes before full files.
- Use `rg` and status scripts before opening broad trees.
- Read referenced docs only when the current decision depends on them.
- Keep templates and examples out of prompts until creating that artifact.
- Summarize long evidence before handing it to another terminal.

## Hard Avoids

- Do not read every skill body just because a workflow mentions skills.
- Do not paste large files into lane or worker prompts when a path reference is enough.
- Do not rely on raw session JSONL as primary state.
- Do not let helper scripts hide failures by returning empty success-shaped output.
- Do not keep increasing skill size when a shared reference or script can hold the detail.

## Budget Tiers

- Direct task: repo instructions, task ledger, targeted code, targeted gate.
- Workstream: direct task context plus design, context manifest, evidence, and related ADRs.
- Lane campaign: workstream context plus lane map, campaign state, worktree status, and shared scopes.
- Program planner: summaries, inventories, lane maps, and state scripts first; open full docs only for
  candidates that may be assigned.

If context is getting heavy, switch to read-only inventory or produce a handoff rather than asking
the user to restate the plan.

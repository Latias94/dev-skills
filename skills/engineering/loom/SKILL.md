---
name: loom
description: Compound Engineering workflow guide and local safety adapter. Use when a Project Compass or `.loom` goal is ready for execution, the user asks for Loom, or Codex needs to route a broad engineering goal through installed `ce-*` skills while preserving repo-local constraints such as worktrees, dirty user changes, exact writable paths, review gates, and verification. Falls back to lightweight lane discovery only when Compound Engineering is unavailable or unsuitable.
---

# Loom

Use Loom as a router and safety adapter for Compound Engineering, not as a competing workflow.

## Core Rule

Prefer the installed Compound Engineering loop for engineering work:

```text
ce-strategy / ce-ideate -> ce-brainstorm -> ce-plan -> ce-work -> ce-code-review -> ce-compound
```

Loom contributes local context: repo instructions, git safety, worktree policy, dirty-state protection,
forbidden files, verification expectations, and fallback lane discovery. Do not copy or vendor CE skill
bodies during normal repo work.

## Workflow

1. Detect CE
   - Treat CE as available only with concrete evidence: loaded `ce-*` skills, `~/.codex/skills/compound-engineering/`, or user confirmation.
   - If CE is missing, recommend installing the full plugin and agent set, then either stop or use the fallback lane map if the user wants to continue now.
2. Attach Local Context
   - Read repo instructions, dirty git state, relevant planning docs, and CE artifacts (`STRATEGY.md`, `CONCEPTS.md`, `docs/brainstorms/`, `docs/plans/`, `docs/solutions/`, `.compound-engineering/`).
   - Read `references/discovery-rules.md` for local safety context before invoking CE on broad or risky work.
3. Route to CE
   - Vague product or requirement work: invoke `ce-brainstorm`.
   - Need an implementation plan or plan deepening: invoke `ce-plan`.
   - Existing CE plan under `docs/plans/`: invoke `ce-work`.
   - Bug with unknown root cause: invoke `ce-debug`, then review and compound.
   - Finished or risky diff: invoke `ce-code-review`; use `mode:agent` when Loom or another caller owns fixes.
   - Verified non-trivial learning: invoke `ce-compound`.
4. Add Safety Rails
   - Pass local constraints explicitly: allowed worktree, branch policy, files that must not be touched, dirty user edits, test command expectations, commit policy, and stop conditions.
   - Use `references/prompt-patterns.md` for copyable CE invocation shapes.
   - Do not let CE-generated plans or workers override repo instructions or user dirty-state protections.
5. Fallback Only When Needed
   - If CE is unavailable, missing agents, or unsuitable for a narrow local operation, read `references/lane-map.md` and produce a lightweight Loom-native lane map.
   - Keep fallback lanes conservative: disjoint writable paths, read-only reviewers, fresh verification, and explicit stop conditions.

## Example

```text
User: Use Loom to implement safer retries.
Loom: detects CE is installed, reads repo git/worktree rules and dirty state, invokes `ce-brainstorm`
if requirements are vague, then `ce-plan` and `ce-work`; it preserves local forbidden files and
requires `ce-code-review` plus fresh verification before closeout.
```

## References

- Read `references/discovery-rules.md` before invoking CE on broad, risky, or dirty work.
- Read `references/prompt-patterns.md` before writing CE invocation prompts or manual handoff prompts.
- Read `references/lane-map.md` only for fallback when CE is unavailable or inappropriate.

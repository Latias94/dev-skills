# Dev Skills Context

## Current Direction

This repository is no longer the source of a Rust workstream workflow. Trellis beta should own active
development workflow, task state, subagent dispatch, context injection, and finish/check loops.

This repository keeps only small reusable Codex skills.

## Retained Local Skills

- `commit-work`
- `codex-session-recovery`
- `humanizer`

Matt-style engineering skills are expected to be installed outside this repository.

## Avoid

- Recreating old workstream queues inside Trellis.
- Keeping legacy machine ledgers as active authority.
- Copying every historical workstream into `.trellis/tasks/`.
- Putting source-code paths into Trellis `implement.jsonl` or `check.jsonl`.

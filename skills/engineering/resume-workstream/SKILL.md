---
name: resume-workstream
description: >
  Resumes a Rust workstream after context loss, a new Codex session, or handoff. Use when the user
  says continue, resume, pick up this workstream, find the next task, or recover the current state
  from WORKSTREAM.json, CONTEXT.jsonl, TODO.md, HANDOFF.md, JOURNAL, evidence docs, and git status.
---

# Resume Workstream

Reconstruct the current lane state and choose the next safe move.

## Read Order

1. `WORKSTREAM.json`
2. `CONTEXT.jsonl`, if present
3. architecture refs named by `WORKSTREAM.json` or `CONTEXT.jsonl`, if any
4. `HANDOFF.md`
5. `TODO.md`
6. `EVIDENCE_AND_GATES.md`
7. newest relevant `JOURNAL/*.md`
8. git status and recent commits

If files disagree, use the source-of-truth order:

1. ADRs
2. architecture maps for capability boundaries
3. workstream design/gates
4. task ledger
5. handoff/journal
6. chat

## Example

```text
Use $resume-workstream to reconstruct docs/workstreams/emulator-mvp and recommend the next task.
```

## Output

Summarize:

- lane status,
- architecture refs, capability tags, and lane slug when present,
- current authoritative docs,
- context manifest health,
- completed tasks,
- blocked tasks,
- next executable task,
- recommended delegated skill (`run-workstream-task`, `review-workstream`,
  `verify-rust-workstream`, `open-workstream`, `close-workstream`, `diagnose`, or `handoff`),
- and whether a Codex goal should be set.

Do not implement before the next task is clear.

---
name: resume-workstream
description: >
  Resumes a Rust workstream after context loss, a new Codex session, or handoff. Use when the user
  says continue, resume, pick up this workstream, find the next task, or recover the current state
  from WORKSTREAM.json, TODO.md, HANDOFF.md, JOURNAL, evidence docs, and git status.
---

# Resume Workstream

Reconstruct the current lane state and choose the next safe move.

## Read Order

1. `WORKSTREAM.json`
2. architecture refs named by `WORKSTREAM.json`, if any
3. `HANDOFF.md`
4. `TODO.md`
5. `EVIDENCE_AND_GATES.md`
6. newest relevant `JOURNAL/*.md`
7. git status and recent commits

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
- completed tasks,
- blocked tasks,
- next executable task,
- recommended delegated skill (`run-workstream-task`, `review-workstream`,
  `verify-rust-workstream`, `open-workstream`, `close-workstream`, `diagnose`, or `handoff`),
- and whether a Codex goal should be set.

Do not implement before the next task is clear.

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
2. `HANDOFF.md`
3. `TODO.md`
4. `EVIDENCE_AND_GATES.md`
5. newest relevant `JOURNAL/*.md`
6. git status and recent commits

If files disagree, use the source-of-truth order:

1. ADRs
2. workstream design/gates
3. task ledger
4. handoff/journal
5. chat

## Example

```text
Use $resume-workstream to reconstruct docs/workstreams/emulator-mvp and recommend the next task.
```

## Output

Summarize:

- lane status,
- current authoritative docs,
- completed tasks,
- blocked tasks,
- next executable task,
- recommended delegated skill (`run-workstream-task`, `open-workstream`, `close-workstream`,
  `diagnose`, or `handoff`),
- and whether a Codex goal should be set.

Do not implement before the next task is clear.

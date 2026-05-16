---
name: rust-workstream
description: >
  Compatibility router for the split workstream skills. Use open-workstream, run-workstream-task,
  resume-workstream, or close-workstream for new workflows. This exists so older prompts that
  mention rust-workstream still route to the appropriate smaller action.
---

# Rust Workstream

Compatibility router. Prefer the smaller action skills:

- `open-workstream` to create or update a durable lane and task ledger.
- `run-workstream-task` to execute one bounded task.
- `resume-workstream` to reconstruct state and choose the next task.
- `close-workstream` to finalize gates, evidence, status, and follow-ons.

If invoked, classify the request and immediately delegate to the narrow skill above. Do not keep
planning or executing inside this compatibility wrapper.

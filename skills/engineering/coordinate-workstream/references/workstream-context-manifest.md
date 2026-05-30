# Workstream Context Manifest

Use a context manifest when a planner prepares a lane goal bundle for long-running terminals or
parallel workers. The manifest is a small JSONL file that points agents to durable context before
they execute; it is not a task list and it does not replace ADRs, workstream docs, or `TODO.md`.

Recommended path:

```text
docs/workstreams/<slug>/CONTEXT.jsonl
```

Format:

```jsonl
{"file":"docs/adr/0001-example.md","reason":"Architecture contract for this lane"}
{"file":"docs/architecture/STORAGE.md","reason":"Storage lane ownership and shared scopes"}
{"file":"docs/workstreams/<slug>/DESIGN.md","reason":"Target state and non-goals"}
{"file":"docs/workstreams/<slug>/EVIDENCE_AND_GATES.md","reason":"Validation gates for acceptance"}
{"file":"docs/workstreams/<slug>/research/topic.md","reason":"Research needed before implementation"}
```

Rules:

- Include ADRs, architecture docs, workstream docs, evidence docs, and research.
- Do not include code files that workers will modify; workers discover code during execution.
- Keep the list short enough to read at lane start. If it grows too large, split the workstream or
  narrow the lane goal bundle.
- Refresh the manifest before assigning a lane goal bundle, after a major design change, and before
  an independent review.
- Treat the manifest as an input hint, not authority. ADRs and workstream docs still outrank it.

Planner usage:

1. Read or create the manifest before assigning a lane terminal.
2. Reference it in the planner prompt and in the terminal record inside planner state.
3. Tell workers which files from the manifest are mandatory for their task.

Lane usage:

1. Read the manifest before choosing the next task.
2. Stop when a needed context file is missing, stale, or contradicts the task ledger.
3. Update the workstream handoff with the context files actually used.

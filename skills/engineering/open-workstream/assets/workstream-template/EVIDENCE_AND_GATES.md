# <Workstream Title> — Evidence And Gates

Status: Draft
Last updated: YYYY-MM-DD

## Smallest Current Repro

```bash
cargo nextest run -p <package> <test-filter>
```

## Gate Set

### Targeted Iteration Gate

```bash
cargo nextest run -p <package> <test-filter>
```

### Package Gate

```bash
cargo nextest run -p <package>
```

### Broader Closeout Gate

```bash
cargo nextest run --workspace
```

Use a narrower closeout gate when the workspace is too large, and explain why.

### Review Gate

Run `review-workstream` before accepting task or lane completion. Record blocking findings, missing
gates, and residual risks here or link to the review note.

## Evidence Anchors

- `docs/workstreams/<slug>/DESIGN.md`
- `docs/workstreams/<slug>/TODO.md`
- `docs/workstreams/<slug>/TASKS.jsonl`
- `docs/workstreams/<slug>/CAMPAIGNS.jsonl`
- `docs/workstreams/<slug>/MILESTONES.md`
- code/test paths proving the shipped behavior

## Notes

Record what each gate proves. Do not list commands without explaining the behavior they cover.

Fresh verification is required before marking a task, Codex goal, or lane complete.

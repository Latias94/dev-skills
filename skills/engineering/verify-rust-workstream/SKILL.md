---
name: verify-rust-workstream
description: >
  Verifies Rust workstream tasks or lanes with fresh command evidence before completion claims.
  Use when a task, Codex goal, worker handoff, workstream lane, or closeout is about to be marked
  done, passing, ready to merge, or complete.
---

# Verify Rust Workstream

Use this before claiming a Rust task or workstream is complete. Evidence must be fresh.

## Inputs

Require or infer:

- workstream path,
- task ID or lane claim,
- changed file/module scope,
- gate set from `EVIDENCE_AND_GATES.md`,
- repo validation preferences from `AGENTS.md`.

If the claim is vague, rewrite it as a concrete statement before running commands.

## Verification Rule

No completion claim without current command evidence.

1. Identify the exact claim.
2. Pick the smallest command that proves it.
3. Run it fresh in the current workspace.
4. Read exit code and output.
5. Record what the command proves in `EVIDENCE_AND_GATES.md`.
6. Report skipped broader gates with a concrete reason.

Old output, worker reports, and "should pass" are not evidence.

## Rust Gate Selection

Prefer non-destructive checks here:

- formatting: `cargo fmt --check` when formatting status is the claim,
- targeted iteration: `cargo nextest run -p <package> <test-filter>`,
- package gate: `cargo nextest run -p <package>`,
- broader gate: `cargo nextest run --workspace`,
- add `cargo clippy` or doc tests when the task changes public API, unsafe code, traits, or docs.

Use narrower closeout gates for huge workspaces only when the reason is recorded.

## Evidence Update

Update `EVIDENCE_AND_GATES.md` with:

- timestamp or date,
- command,
- scope,
- result,
- behavior proven,
- any gate not run and why.

Do not mark `TODO.md` complete, close a Codex goal, or close a lane when required gates fail.

## Example

```text
Use $verify-rust-workstream to verify task EMU-020 in docs/workstreams/emulator-mvp before marking
the task and Codex goal complete.
```

## Output

Report:

- claim verified or not verified,
- commands run and results,
- evidence file updates,
- gates skipped with reasons,
- blockers and next action.

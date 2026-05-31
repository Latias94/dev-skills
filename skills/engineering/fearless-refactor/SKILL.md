---
name: fearless-refactor
description: Turns architecture-review findings into a durable Rust refactoring execution lane. Use when the user wants fearless refactoring after improve-codebase-architecture, modular boundaries, deletion of redundant code, future-facing Rust architecture, or a dev-flow-backed refactor plan.
---

# Fearless Refactor

Convert architecture findings into disciplined refactoring execution. This skill is for the moment
after `$improve-codebase-architecture` has found deepening opportunities and the user wants to act.

The bias is to remove accidental complexity early instead of preserving it until a future rewrite,
while still using the repository's workflow docs, tests, and review gates.

## Operating Principles

- Prefer the correct long-term shape over tiny local patches when the codebase is not constrained
  by compatibility, release, or migration risk.
- Delete redundant code, pass-through modules, stale abstractions, and obsolete compatibility paths
  when evidence shows they no longer earn their keep.
- Deepen modules: smaller interfaces, richer implementations, clearer seams, and better locality.
- Keep Rust boundaries explicit: crates, modules, traits, ownership, error types, feature flags, and
  tests should communicate the architecture.
- Do not invent abstractions for hypothetical adapters. One adapter is a smell; two adapters can
  justify a seam.
- Preserve behavior with tests and fresh validation before claiming success.

## Process

1. Gather context:
   - The `$improve-codebase-architecture` report or selected candidate.
   - `CONTEXT.md`, relevant ADRs, active workstreams, and existing validation commands.
   - Current git status, so user changes are protected.
2. Select the smallest workflow scale that fits:
   - Small local cleanup -> `tdd` or `diagnose`, with a short refactor brief.
   - Multi-step or cross-crate refactor -> `open-workstream`.
   - Long-lived capability ownership across workstreams -> `run-architecture-lane`.
3. Strengthen the refactor brief before coding:
   - Target module boundary.
   - Code to delete.
   - Interfaces to shrink.
   - Tests that should move to the interface.
   - Compatibility and migration constraints.
   - Validation commands, preferring `cargo fmt` and `cargo nextest` for Rust repos.
4. Ask whether to create a Codex goal when the scope is a bounded task from `TODO.md` or one
   approved lane goal bundle. Do not set a goal for an entire architecture lane.
5. Delegate through `$dev-flow` with a concrete phase transition:
   - planning -> `open-workstream` for a new durable lane,
   - lane execution -> `run-architecture-lane` for large capability-scoped terminals,
   - execution -> `run-workstream-task` for one task,
   - review -> `review-workstream`,
   - verification -> `verify-rust-workstream`,
   - closeout -> `close-workstream`.
6. If the user explicitly authorizes autonomous commits, commit only after the bounded task is
   reviewed and verified:
   - stage only files changed for that task,
   - exclude unrelated user changes,
   - inspect the staged diff,
   - use a Conventional Commit message,
   - report the commit hash and validation evidence.

## Refactor Brief

Before implementation starts, produce this brief:

- **Intent**: what future complexity this removes.
- **Scope**: files, crates, modules, and public surfaces involved.
- **Deletion plan**: dead code, pass-through layers, redundant abstractions, and obsolete docs to
  remove.
- **Boundary plan**: target modules, seams, adapters, trait ownership, and dependency direction.
- **Testing plan**: interface-level tests, regression coverage, and validation commands.
- **Risk plan**: migrations, compatibility risks, performance risks, and rollback signals.
- **Workflow plan**: whether this becomes a workstream, a task-ledger item, or a small direct change.
- **Scale plan**: direct task, workstream, or architecture lane.

## Output Contract

When handing off to `$dev-flow`, say:

- current phase,
- delegated skill,
- expected artifact,
- where the artifact will live,
- whether a Codex goal is recommended,
- and the next likely phase.

## Example

```text
Use $fearless-refactor on the top recommendation from the architecture report. Turn it into a dev-flow workstream, delete redundant modules where justified, and explicitly ask whether this terminal should set a Codex goal for the first bounded task.
```

```text
Use $fearless-refactor for this architecture lane. After each verified bounded task, commit only your changes with a Conventional Commit message and report the commit hash.
```

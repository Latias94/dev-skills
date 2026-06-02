---
name: commit-work
description: >
  Create safe, reviewable git commits with intentional staging and Conventional Commit messages.
  Use when the user asks Codex to commit work, craft a commit message, stage changes, split changes
  into logical commits, or verify what belongs in a commit.
---

# Commit Work

Create commits that are easy to review, safe to merge, and scoped to the user's intent.

## Read First

- repo `AGENTS.md` or local git rules,
- `git status --short --branch`,
- unstaged and staged diffs: `git diff --stat`, `git diff`, `git diff --cached --stat`,
- relevant task, spec, ADR, or evidence docs when committing scoped project work.

## Workflow

1. Confirm the user asked to commit or explicitly approved committing.
2. Inspect all changed and untracked files before staging.
3. Split unrelated changes into separate commits. Split by feature/refactor, logic/tests, docs/code,
   dependency/config changes, formatting, or unrelated task scopes.
4. Stage only intended paths or hunks. Prefer precise pathspecs; use patch staging only when mixed
   changes in one file must be separated.
5. Review staged content with `git diff --cached` before committing.
6. Check for secrets, debug logging, unrelated formatting churn, generated files, and user changes
   that were not part of the requested commit.
7. Run the smallest relevant verification unless the user asks to skip it or the repo rules define a
   different gate.
8. Commit with Conventional Commits.
9. Report commit hash, message, staged scope, verification, skipped checks, and remaining dirty
   files.

## Guardrails

- Do not use `git add .` or `git add -A` until every dirty file has been inspected and belongs.
- Do not discard, restore, reset, checkout, clean, or stash user changes while preparing a commit.
- If you need to unstage, unstage only from the index and leave the working tree intact.
- Do not commit failed gates, unrelated dirty files, unresolved `DONE_WITH_CONCERNS`, secrets, or
  planner-blocked shared-scope changes.
- When changes belong to different task or feature scopes, commit only the approved scope and
  report what remains.

## Message Shape

Use `references/commit-message-template.md`.

Prefer:

```text
type(scope): concise imperative summary

Explain what changed and why when the summary is not enough.
```

Use `BREAKING CHANGE:` footer or `!` when the contract changes.

## Example

```text
Use $commit-work to commit the reviewed storage VFS health changes only. Follow repo git rules,
stage only approved files, use Conventional Commits, and report remaining dirty files.
```

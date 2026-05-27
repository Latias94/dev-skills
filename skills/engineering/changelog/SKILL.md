---
name: changelog
description: Maintain release notes in Keep a Changelog style for SemVer projects. Use when updating CHANGELOG.md, preparing a release, comparing commits since the latest tag, or turning git history into user- and developer-facing release notes.
---

# Changelog

Maintain `CHANGELOG.md` as a release communication artifact, not a commit log.

Use the format from Keep a Changelog, and assume the project adheres to Semantic Versioning unless
the repository documents a different release policy.

## Process

1. Read the release context:
   - `CHANGELOG.md`, release docs, package metadata, and existing tag style.
   - `git tag --sort=-creatordate` or an equivalent command to identify the latest relevant tag.
   - Commits and diffs from the latest tag to `HEAD`.
2. Audit whether meaningful changes since the latest tag are already represented in
   `CHANGELOG.md`.
3. Group changes under Keep a Changelog categories:
   - `Added`
   - `Changed`
   - `Deprecated`
   - `Removed`
   - `Fixed`
   - `Security`
4. Write for readers:
   - Users should understand visible behavior, migration impact, and upgrade risk.
   - Developers should understand API, configuration, data format, and operational impact.
   - Avoid internal-only implementation details, noisy file names, task IDs, and commit-by-commit
     narration unless they explain user-visible behavior.
5. Deduplicate aggressively:
   - Merge repeated bullets that describe the same capability.
   - Keep one strongest wording for each change.
   - Do not list refactors unless they affect public behavior, maintainability promises,
     performance, reliability, security, or developer workflow.
6. Add examples when they help adoption:
   - For new APIs, CLIs, config keys, or workflows, add a compact code example.
   - Prefer links to existing examples or docs when the repository already has them.
7. Preserve style:
   - Match existing heading levels, date format, link references, and version ordering.
   - Do not manually hard-wrap prose or bullets; let Markdown wrap naturally.

## Release Triage

Use SemVer language when sorting impact:

- `major` for breaking API, CLI, config, protocol, data, or behavior changes.
- `minor` for backward-compatible features.
- `patch` for backward-compatible fixes and documentation corrections.

If a breaking change is present, make migration notes explicit. If no public change exists, say so
instead of inventing release notes.

## Finalize Release

When the user is preparing an actual release:

1. Move the curated `Unreleased` entries into a version heading with the release date.
2. Keep empty `Unreleased` scaffolding only if the project already does that.
3. Check that compare links match the repository's existing style:
   - `Unreleased` should compare the new version tag to `HEAD`.
   - The new version should compare the previous release tag to the new release tag.
4. Confirm the chosen SemVer bump against the changelog content.
5. Do not create tags or publish releases unless the user explicitly asks.

## Output Contract

When editing a changelog, report:

- latest tag and compared range,
- changelog sections updated,
- notable commits intentionally omitted and why,
- examples or docs links added,
- remaining release risks or versioning questions.

## Example

```text
Use $changelog to update CHANGELOG.md for the next release. Compare HEAD to the latest tag, remove duplicate entries, keep the notes user-facing, and add a short example for any new public API.
```

```text
Use $changelog to finalize version 1.4.0 from Unreleased, set today's release date, update compare links, and confirm whether the entries justify a minor release.
```

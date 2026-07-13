---
name: repo-changelog
description: Write concise, user-facing changelogs and release notes from verified repository deltas. Use when a version or Unreleased section must be drafted, updated, or finalized with linked PRs/issues, migration notes, and contributor credit.
---

# Repo Changelog

Treat a release as a **release delta**: final user-visible outcomes between `BASE` and `TARGET`, not a commit transcript.

## Workflow

1. Establish the release contract.
   - Read repository instructions, the changelog, release docs, package metadata, and the nearest comparable release section.
   - Confirm the output target, `BASE`, `TARGET`, version, date, audience, and publication boundary. A state is published when that audience could consume and rely on it through a release, prerelease, registry artifact, or deployment. Partition the work when the range crosses a publication boundary.
   - Infer a missing base only when one reachable tag is clearly correct; prereleases normally compare with the preceding prerelease. For `Unreleased`, keep `BASE` at the last applicable publication boundary and reconcile the whole section on every update. Ask before drafting when refs fail, multiple bases remain plausible, or `BASE` is not an ancestor of `TARGET`.
   - Preserve the repository's headings, ordering, voice, date format, link style, and version-link convention. Use Keep a Changelog categories only when no local convention exists.
   - Completion: both refs resolve, the range and publication boundary are explicit, and the target format is identified.

2. Build an outcome ledger from evidence.
   - Start with the total `BASE..TARGET` diff and changed-path inventory. Use first-parent history to find integration themes, then inspect relevant commits, PRs, public APIs, docs, tests, manifests, and advisories.
   - Record each candidate as `surface | BASE state | TARGET state | audience exposure | impact/action | refs | contributor | section | absorbed into | disposition`. Treat a verified merged PR as an evidence unit, not necessarily as a changelog item; inspect individual commits when no PR owns them or the final state remains ambiguous.
   - Read [Evidence and attribution](references/evidence-and-attribution.md) when classifying publication state or when the range has merge noise, GitHub PRs/issues, external contributors, persistent effects, or security work.
   - Completion: every material user-facing change is supported by evidence, and every inspected item is accounted for.

3. Consolidate the final state.
   - Compare each public surface at `BASE` and `TARGET`. When a capability is introduced and then fixed, refactored, or renamed before its first publication, publish one outcome describing its final form; fold all material references and contributor credit into that outcome.
   - Treat behavior present at `BASE`, or exposed across an applicable publication boundary, as an existing contract. Its later fix, rename, deprecation, or removal is a separate outcome with migration guidance where required.
   - Keep fully reverted or semantically unchanged work in the ledger as `net-zero` and publish no item unless audience exposure or persistent data, migration, artifact, security, or operational effects remain. Describe only the surviving behavior after a partial revert.
   - Merge commits and PRs that produce one user outcome. Mark intermediate, superseded, and duplicate work as `folded-into` rather than emitting separate items; preserve their verified references and credit in the final outcome.
   - Include internal refactors, tests, CI, and dependency work only when their net effect relative to the publication boundary changes security, compatibility, reliability, performance, packaging, or a developer-facing workflow.
   - Give each outcome one home. Keep an introduction thematic; do not repeat its feature list in Highlights or category sections.
   - Surface breaking, deprecated, removed, and security-sensitive behavior with the affected audience and a concrete migration, upgrade, or mitigation action.
   - Completion: each included outcome appears exactly once and has one non-overlapping section.

4. Write for the user.
   - Lead with what users can now do, what behaves differently, or what problem is fixed. Retain public command, option, package, API, and configuration names only when they help users act.
   - Keep every prose paragraph and list item on one physical Markdown line; let the renderer wrap it. Keep code blocks in their natural format.
   - Use only non-empty sections, order items by user impact rather than commit chronology, and use the shortest wording that preserves constraints and required action.
   - Attach verified PR and issue references to the most specific item, sorted and deduplicated. Follow a proven repository-native reference style; otherwise use explicit Markdown links.
   - Credit a contributor once, either beside the related item or in one Contributors section. Use verified PR author and explicit co-author handles that materially contributed; distinguish contributions from issue reports when the repository does.
   - Completion: the draft is concise, user-facing, single-line formatted, linked, and attributed without unsupported claims.

5. Verify before finishing.
   - Trace every bullet back to the ledger and final diff; confirm all links, contributor identities, version/date data, and migration commands.
   - Scan the whole release section for semantic repetition, separate fix/refactor bullets for capabilities first published by that same section, empty headings, raw commit narration, internal jargon, manual wrapping, and accidentally disclosed private security details.
   - Confirm all external PR authors, material co-authors, and credited reporters appear once or have an explicit exclusion reason in the working ledger.
   - Reconcile an editable `Unreleased` section to the final outcome ledger. Keep published sections as historical snapshots; change one only to correct a factual error, and put later behavior changes in the next release section.
   - When editing a file, keep the diff scoped to the intended release section and required compare links.
   - Report the range, updated sections, meaningful exclusions, unresolved evidence gaps, and release risks. Create tags or publish releases only when explicitly requested.
   - Completion: every gate above passes or the remaining uncertainty is reported instead of guessed.

## Example

```text
Use $repo-changelog to update CHANGELOG.md for v1.6.0 from v1.5.2..HEAD. Describe each user-visible outcome once, keep every bullet on one physical line, link verified PRs and issues, credit contributors, and make required migrations prominent.
```

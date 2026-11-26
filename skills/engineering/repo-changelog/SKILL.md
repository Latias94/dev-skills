---
name: repo-changelog
description: Write concise, user-facing changelogs and release notes from verified repository deltas. Use when a version or Unreleased section must be drafted, updated, or finalized with linked PRs/issues, migration notes, package projections, and contributor credit.
---

# Repo Changelog

Treat a release as a **release delta**: final user-visible outcomes between `BASE` and `TARGET`, not a commit transcript.

## Workflow

1. Establish the release contract.
   - Read repository instructions, root and in-scope package changelogs, release docs, package metadata, the nearest comparable release section, and any repository-owned changelog parsers or verifiers.
   - Confirm target file(s), mode (`changelog`, `release-note`, or `package-projection`), `BASE`, `TARGET`, version, date, publication boundary, repository archetype (product, CLI/tool, library/SDK, or hybrid monorepo), downstream renderers (repo Markdown, verbatim GitHub Release extraction, or package registries), and the `Unreleased` lifecycle policy (keep empty heading vs. date/remove before release freeze).
   - Keep one verified outcome ledger across root notes and all requested projections. Read [Projections and portability](references/projections-and-portability.md) when adapting to repository archetypes, updating sub-package/platform changelogs, or publishing to external renderers.
   - Read [Release-note presentation](references/release-note-presentation.md) when producing `release-note` mode, adding Highlights, or structuring thematic editorial sections.
   - Infer a missing base only when one reachable tag on the same release line and tag prefix is clearly correct; sort SemVer prereleases before stable. For `Unreleased`, keep `BASE` at the last applicable publication boundary and reconcile the whole section on every update. Ask before drafting when refs fail, multiple bases remain plausible, or `BASE` is not an ancestor of `TARGET`.
   - Preserve the repository's headings, ordering, voice, date format, link style, and version-link convention. Use Keep a Changelog categories only when no local convention exists.
   - Completion: refs resolve on the right release line, automation/renderer contracts are known, and the target format is identified.

2. Build an outcome ledger from evidence.
   - Start with the total `BASE..TARGET` diff, public surface inventory, and `--first-parent` history to identify integration themes before drilling into inner commits, PRs, public APIs, manifests, docs, migrations, and advisories.
   - Record each candidate as `surface | BASE state | TARGET state | introduced-in-range? | audience exposure | impact/action | refs | contributor | section | absorbed into | disposition`. Treat a merged PR as an evidence unit, not automatically as one bullet: unpack umbrella/integration PRs into distinct outcomes, and inspect direct commits when no PR owns them.
   - Read [Evidence and attribution](references/evidence-and-attribution.md) for release-line tag queries, the `BASE`-existence test, large-refactor distillation, efficient GitHub PR lookups, bounded metric/security claims, and contributor credit.
   - Completion: every material user-facing change has verified evidence and every inspected change is accounted for.

3. Consolidate the final state and filter noise.
   - Apply the `BASE`-existence test to every `fix`, `refactor`, and `perf` change: could a user on `BASE` observe the bug or old behavior?
     - If **no** (it fixed or refined a capability or mid-refactor regression introduced *after* `BASE`), **never** emit a separate `Fixed` item: fold it (`folded-into`) into the owning new/changed outcome while preserving verified references and credit, or drop it as `net-zero`/`internal-only` when `BASE` and `TARGET` behave equivalently.
     - If **yes** (a user on `BASE` or an earlier publication boundary could observe it), publish the net `Fixed`, `Changed`, `Deprecated`, or `Removed` outcome with required migration guidance.
   - Distill large refactors into user-visible deltas only. Omit internal crate splits, module moves, test/benchmark/CI rewrites, and dependency bumps unless their net effect changes public imports, feature flags, ABI/schema/MSRV contracts, packaging, security, reliability, or measurable performance.
   - Keep fully reverted or semantically unchanged work in the ledger as `net-zero` unless audience exposure or persistent data, migration, artifact, security, or operational effects remain. Describe only surviving behavior after a partial revert.
   - Synthesize clusters of related performance, parity, or cleanup commits into user-level outcomes rather than narrating commits. Give each outcome one detailed home; any `release-note` Highlight must remain summary-only and non-conflicting.
   - Completion: no `Fixed` item describes a post-`BASE` regression, internal refactor noise is excluded, and every included outcome has one detailed home.

4. Prioritize and write for the target audience.
   - Order and weight by user urgency: (1) breaking changes, coupled upgrade/rebuild actions, MSRV/runtime floors, deprecations/removals, and security advisories with exposure context; (2) headline capabilities and default shifts; (3) real `BASE` fixes and bounded performance/quality wins; (4) downstream builder/tooling notes only when actionable.
   - Match the repository archetype: libraries/SDKs lead with API/ABI/feature/MSRV contracts; products/CLIs lead with user workflows, outputs, defaults, and runnable examples; hybrid monorepos separate user workflows from integrator migrations and project binding-specific symbols into package changelogs.
   - Lead every item with what users can now do, what changed, or what was fixed; cite public identifiers only when they help users act. Back every performance or size claim with baseline, workload, and environment; never claim unpublished or deferred channels are available, and keep CI/upload receipts out of user notes.
   - Keep every prose paragraph and list item on one physical Markdown line (never wrap links or attribution onto indented continuation lines). Keep code blocks natural and use safe fence tags when renderers auto-render diagram languages.
   - Use only non-empty sections, order items by user impact, and add consistent subsystem/crate prefixes when a section grows long (roughly 8+ items).
   - Attach verified PR/issue links sorted and deduplicated, using portable absolute URLs whenever output is extracted verbatim to GitHub Releases or package registries without link rewriting. Credit each contributor once, using canonical handles and distinguishing reports from contributions when local style does.
   - Completion: the draft is prioritized for its audience, bounded, single-line formatted, link-portable, and accurately attributed.

5. Verify before finishing.
   - Trace every bullet back to the ledger and final diff; re-check that no `Fixed` item belongs to a newly introduced feature or mid-refactor churn, and check for uncontrolled repetition, empty headings, raw commit narration, internal jargon, manual wrapping, or unapproved security details.
   - Verify every external link, anchor, relative path, and image URL works in every destination renderer (repo view, GitHub Release, registries).
   - Confirm external PR authors, material co-authors, and credited reporters appear once or have an explicit exclusion reason in the ledger.
   - Reconcile `Unreleased` according to the repository's lifecycle rule and check every in-scope package/platform changelog so shipped items do not remain stale under `[Unreleased]`. Keep published historical sections unchanged except to fix factual errors.
   - Run repository-owned changelog/release validators when present, and keep edits scoped to the intended release section(s) and required compare links.
   - Report the range, updated files/sections, meaningful exclusions (including absorbed post-`BASE` fixes and internal-only refactors), unresolved gaps, and release risks. Create tags or publish releases only when explicitly requested.
   - Completion: every gate passes or remaining uncertainty is reported instead of guessed.

## Example

```text
Use $repo-changelog to prepare v0.12.0 from v0.11.0..HEAD across root CHANGELOG.md and in-scope platform changelogs. Filter tags with v*, apply the BASE-existence test so post-v0.11.0 feature fixes and internal crate refactors stay absorbed or omitted, prioritize breaking/ABI migrations and user outcomes, verify link portability for GitHub Releases, and run the repo changelog validator.
```

# Evidence and Attribution

Use this reference to turn repository history into a complete evidence ledger without treating history as the changelog.

## Establish the Range

Honor explicit refs first. Verify them and their relationship:

```shell
git rev-parse --verify "$BASE^{commit}"
git rev-parse --verify "$TARGET^{commit}"
git merge-base --is-ancestor "$BASE" "$TARGET"
```

Stop and ask for the intended range when either ref is missing, the ancestry check fails, or multiple release-line bases remain plausible.

When the base is absent, scope tag discovery to the release line's tag prefix (for example `v*` for a workspace release, or `<pkg>-v*` for an independently versioned package) so sibling channel or package tags (such as `flutter-v*` or `tree-sitter-mermaid-v*`) are never selected as the base. Always pass `-c versionsort.suffix=-` when sorting SemVer tags so prereleases sort before their corresponding stable release:

```shell
git describe --tags --match "${TAG_PREFIX}*" --abbrev=0 "$TARGET^"
git -c versionsort.suffix=- tag --merged "$TARGET" --list "${TAG_PREFIX}*" --sort=-version:refname
```

For a maintenance branch (such as `v0.9.4` branched from `v0.9.3`), verify the base against that maintenance line's prior tag rather than a newer minor line. For incremental prereleases, compare against the preceding prerelease on the same line.

Establish the publication boundary separately from Git ancestry. A merge or tag is not automatically a publication, while a prerelease, registry artifact, continuous deployment, or other audience-accessible state can be one. If `BASE..TARGET` crosses a boundary applicable to the target audience, partition the range rather than folding outcomes across it. Cumulative stable notes may summarize prerelease work as one final outcome only when the repository's established convention does so; incremental prerelease notes still describe changes since the prior prerelease.

## Gather Final-State Evidence

Use the complete range diff as the source-state baseline. Use history to explain intent, find related reviews, assign credit, and detect intermediate audience exposure or persistent effects that the final source tree cannot show.

```shell
git diff --name-status "$BASE..$TARGET"
git diff --stat "$BASE..$TARGET"
git log --first-parent --oneline "$BASE..$TARGET"
git log --format='%H%x09%an%x09%ae%x09%s' "$BASE..$TARGET"
```

In large ranges (100+ commits), do not read commits linearly from oldest to newest as a draft outline:

1. Inventory changed public surfaces first (manifests, Cargo features, public exports/headers, CLI flags, schemas, docs, migrations, and security advisories).
2. Group `--first-parent` merges and direct commits into integration themes.
3. Unpack umbrella or integration PRs (a single PR carrying dozens of unrelated fixes or migrations) by inspecting their inner commits and final diff so each distinct user-facing outcome gets its own ledger entry.
4. Keep dispositions (`included`, `folded-into`, `internal-only`, `superseded`, `duplicate`, `net-zero`, `outside-range`) in the working ledger, never in the published changelog.

## Apply the `BASE`-Existence Test and Distill Large Refactors

Commit prefixes (`fix:`, `refactor:`, `perf:`) describe author intent at commit time, not user-visible release deltas. Before placing any item in the changelog, verify whether the affected surface or bug existed at `BASE` (for example with `git show "$BASE:<path>"` or checking whether the symbol, flag, schema, or file existed at `BASE`):

| Change origin in `BASE..TARGET` | Observable on `BASE`? | `TARGET` differs for users? | Ledger disposition and changelog treatment |
| --- | --- | --- | --- |
| New capability added in range, followed by bug fixes, renames, or tuning | No | Yes (final new capability) | Publish one final `Added` outcome. Mark all follow-up fixes/refactors `folded-into` it and carry forward their PR refs and contributor credit. Never emit separate `Fixed` bullets. |
| Regression introduced during an internal refactor and fixed later in the same range | No | No | Record `net-zero` / `internal-only`. Publish nothing. |
| Bug present at `BASE` (or an earlier published boundary) on a surviving surface | Yes | Yes | Record `included` under `Fixed`. |
| Bug present at `BASE` on a surface replaced by a breaking rewrite | Yes | Replaced | Fold into the replacement's `Changed`/migration outcome if the old bug is moot; mention separately only if upgrading users need to know. |
| Large internal refactor (crate splits, module moves, internal IR/pipeline rewrites, test/bench/CI cleanup) | N/A | No public delta | Record `internal-only`. Publish nothing. |
| Large refactor that changes public imports, Cargo features, ABI/schema, MSRV, packaging, or verified perf/size | N/A | Yes | Publish only the public contract delta, required migration action, or bounded measurable win. Do not narrate internal restructuring. |
| Cluster of `perf` or parity commits across one subsystem | Yes | Yes (cumulative) | Synthesize into one to three user-workload outcomes rather than listing each micro-optimization. |

For a source-level revert, check deployed artifacts, persistent data and schema migrations, security exposure, generated files, external side effects, and operational actions before calling it `net-zero`. For absorbed work, set `absorbed into` to the surviving outcome and carry forward every material PR/issue reference and contributor credit.

## Bound Performance, Size, and Security Claims

- **Performance and size metrics**: cite numbers only when verified against the target behavior, and always state the comparison baseline, representative workload/corpus, and host/environment (for example OS, architecture, browser, or runtime). Never write unmeasured superlatives or mix incompatible feature defaults.
- **Security dependency bumps**: state the minimum fixed dependency version, the advisory identifier (such as `RUSTSEC-...` or `CVE-...`), and whether this project's public entrypoints were actually exposed when known.
- **Availability truth**: never copy CI run logs, upload counts, or recovery history into user-facing notes, and never claim a channel or prebuilt artifact is available unless delivery is verified.

## Verify GitHub Relationships

Identify the canonical repository before constructing links:

```shell
gh repo view --json nameWithOwner,url
```

Prefer batch and first-parent discovery before per-commit API calls (especially in ranges with 50+ commits):

1. Extract PR numbers from `--first-parent` merge subjects (`Merge pull request #N` / `(#N)`) and verify them with `gh pr view`.
2. For remaining commits without obvious PR ownership, query merged PRs in the date window (`gh pr list --state merged --limit 100 --json number,title,mergeCommit,mergedAt,baseRefName,url,author`) or fall back to commit-level lookup only for unmapped commits:

```shell
SHA=<commit-hash>
gh api "repos/{owner}/{repo}/commits/$SHA/pulls" --jq '.[] | select(.merged_at != null) | {number, title, state, merged_at, base: .base.ref, merge_commit_sha, url: .html_url, author: .user.login}'
```

Inspect each candidate rather than inferring relationships from similar titles or branch names. Accept it only when it is merged and its merge commit or associated commit belongs to `BASE..TARGET` on the intended release line:

```shell
gh pr view NUMBER --json number,title,url,author,body,state,mergedAt,baseRefName,mergeCommit,closingIssuesReferences,commits
gh issue view NUMBER --json number,title,url,author
```

Treat an issue as related when PR metadata, closing references, or reviewed discussion establishes the relationship. Place references at the end of the relevant item, sorted and deduplicated. When one umbrella PR carries nearly every change in a release, follow repository convention: linking the umbrella PR once on the release intro while reserving per-bullet links for specific feature/fix PRs, issues, and external contributions avoids repeating the same link across dozens of bullets.

Use the repository's bare `#123` style only when every destination renderer resolves it; otherwise emit explicit links to `/pull/123` or `/issues/123`.

## Assign Credit

- Use the merged PR's `author.login` as its canonical author and include explicit co-author handles that materially contributed, even when a PR owns the work.
- Normalize aliases by account rather than commit display name or email.
- Credit an issue reporter only when the report materially led to the outcome and the repository's style credits reports.
- Follow the repository's bot and maintainer-credit policy. In the absence of one, omit automated accounts and credit external human contributions.
- Use inline credit or one Contributors section, not both. Combine multiple related references so the same contribution is thanked once.
- Keep inline attribution on the same physical Markdown line as its bullet; never wrap `Thanks to @user` onto an indented continuation line.
- For private security reports, publish credit only after disclosure is approved and the fix or advisory is public.

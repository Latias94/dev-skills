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

When the base is absent, find the nearest tag before the target, then verify it against tags reachable from the target and the repository's release line. A prerelease normally follows the previous prerelease, not the last stable tag.

```shell
git describe --tags --abbrev=0 "$TARGET^"
git tag --merged "$TARGET" --sort=-version:refname
```

Establish the publication boundary separately from Git ancestry. A merge or tag is not automatically a publication, while a prerelease, registry artifact, continuous deployment, or other audience-accessible state can be one. If `BASE..TARGET` crosses a boundary applicable to the target audience, partition the range rather than folding outcomes across it. Cumulative stable notes may summarize prerelease work as one final outcome only when the repository's established convention does so; incremental prerelease notes still describe changes since the prior prerelease.

## Gather Final-State Evidence

Use the complete range diff as the source-state baseline. Use history to explain intent, find related reviews, assign credit, and detect intermediate audience exposure or persistent effects that the final source tree cannot show.

```shell
git diff --name-status "$BASE..$TARGET"
git diff --stat "$BASE..$TARGET"
git log --first-parent --oneline "$BASE..$TARGET"
git log --format='%H%x09%an%x09%ae%x09%s' "$BASE..$TARGET"
```

Inspect diffs for public surfaces and supporting evidence such as tests, docs, package manifests, migration guides, and advisories. In a large range, first classify every changed path and merged PR; treat a verified PR as an evidence unit and inspect its inner commits when ownership, exposure, persistent effects, or final behavior is unclear. Keep dispositions such as `included`, `folded-into`, `internal-only`, `superseded`, `duplicate`, `net-zero`, or `outside-range` in the working ledger, not in the changelog.

Classify each public surface by its states at the publication boundary:

| BASE state | TARGET state | Default release treatment |
| --- | --- | --- |
| Absent | Present | Publish one final `Added` outcome. Fold same-boundary fixes, refactors, and renames into it. |
| Present | Changed or absent | Publish the net `Changed`, `Fixed`, `Deprecated`, or `Removed` outcome, with required action. |
| Absent | Absent | Record `net-zero` and publish nothing unless audience exposure or persistent effects remain. |
| Semantically equal | Semantically equal | Publish nothing unless an applicable audience observed the intermediate state. |

For a source-level revert, check deployed artifacts, persistent data and schema migrations, security exposure, generated files, external side effects, and operational actions before calling it `net-zero`. For absorbed work, set `absorbed into` to the surviving outcome and carry forward every material PR/issue reference and contributor credit.

## Verify GitHub Relationships

Identify the canonical repository before constructing links:

```shell
gh repo view --json nameWithOwner,url
```

For a commit whose PR is not already verified, assign its hash to `SHA`, query associated pull requests, retain merged candidates, and deduplicate the returned PR numbers:

```shell
SHA=<commit-hash>
gh api "repos/{owner}/{repo}/commits/$SHA/pulls" --jq '.[] | select(.merged_at != null) | {number, title, state, merged_at, base: .base.ref, merge_commit_sha, url: .html_url, author: .user.login}'
```

Inspect each candidate rather than inferring relationships from similar titles or branch names. Accept it only when it is merged and its merge commit or associated commit belongs to `BASE..TARGET` on the intended release line:

```shell
gh pr view NUMBER --json number,title,url,author,body,state,mergedAt,baseRefName,mergeCommit,closingIssuesReferences,commits
gh issue view NUMBER --json number,title,url,author
```

Treat an issue as related when the PR metadata, closing references, or reviewed discussion establishes the relationship. Use the repository's existing bare `#123` style only when the destination renderer resolves it; otherwise emit an explicit link to `/pull/123` or `/issues/123`. Place all references at the end of the relevant item, sorted and deduplicated.

## Assign Credit

- Use the merged PR's `author.login` as its canonical author and include explicit co-author handles that materially contributed, even when a PR owns the work.
- Normalize aliases by account rather than commit display name or email.
- Credit an issue reporter only when the report materially led to the outcome and the repository's style credits reports.
- Follow the repository's bot and maintainer-credit policy. In the absence of one, omit automated accounts and credit external human contributions.
- Use inline credit or one Contributors section, not both. Combine multiple related references so the same contribution is thanked once.
- For private security reports, publish credit only after disclosure is approved and the fix or advisory is public.

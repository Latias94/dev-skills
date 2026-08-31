# Release-Note Presentation

Use this reference only for a curated release announcement. The changelog remains the durable, canonical record of notable release outcomes; the release note helps a reader decide whether to upgrade and where to look next.

## Decide Whether Highlights Help

Add Highlights when the release is a substantial prerelease, changes several public surfaces, introduces a major capability, or requires important migration work. Skip them for routine patches and small single-purpose releases.

Choose three to six outcomes with the largest user impact. A Highlight is a one-sentence summary, not a second full changelog item. Keep API names, references, caveats, and migration commands in the outcome's detailed home.

## Recommended Shape

Adapt the headings to the repository's established style:

1. **Release verdict**: one short paragraph describing the release's purpose, maturity, and availability.
2. **Highlights**: three to six skimmable outcomes, ordered by user impact.
3. **Upgrade first**: only the breaking changes, compatibility constraints, or operational actions readers must handle before adopting the release.
4. **Detailed changes**: repository-native categories or user domains, with each outcome described fully once.
5. **Availability and known limitations**: publication state, experimental surfaces, platform gaps, or bounded residuals that affect adoption.
6. **Contributors**: only when the repository does not already attach credit to detailed items.

Omit empty sections. Small releases may need only a verdict and detailed changes.

## Use Controlled Repetition

Controlled repetition is useful when a reader needs both a fast summary and an actionable record:

- A Highlight states the outcome and user benefit in one sentence.
- `Upgrade first` states the required action without retelling implementation details.
- The detailed item owns names, constraints, references, contributor credit, and the complete migration explanation.

Do not repeat the same full bullet, code sample, or reference list across sections. If two summaries could disagree, remove one and keep the detailed home.

## Show Change When It Clarifies Action

Use a short before/after example for a high-impact API or configuration migration when prose is less clear. Use an image only when behavior is genuinely visual. Do not add decorative galleries, badges, sponsor sections, or emoji unless they are already part of the project's release voice.

## Template

```markdown
## Version

One-paragraph release verdict.

### Highlights

- User-visible outcome and benefit.

### Upgrade first

- Required action; see the detailed breaking-change item for the complete contract.

### Detailed changes

- Canonical outcome with precise names, constraints, references, and credit.

### Availability and known limitations

- Publication state or adoption-relevant limitation.
```

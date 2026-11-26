# Projections and Portability

Use this reference when tailoring changelogs to a repository's audience, maintaining multi-package or multi-platform projections, or ensuring links and formatting survive external release renderers.

## Tailor Priority and Framing to Repository Archetype

Readers arrive at a changelog in descending order of urgency:

1. **Must act / Risk**: breaking API, CLI, schema, or ABI changes; coupled crate/artifact rebuilds; MSRV or minimum runtime bumps; security advisories (with reachability context); deprecations, removals, and output/snapshot shifts.
2. **Headline value**: major new capabilities, flagship default changes, and architectural work that unlocks concrete user benefits (speed, footprint, new targets, composable features).
3. **Everyday quality**: real bugs fixed since `BASE`, bounded performance/memory wins, and ergonomic or coverage improvements.
4. **Supporting builder notes (low priority, omit if irrelevant)**: repository dev/CI toolchain bumps (explicitly distinguished from library MSRV), packaging/docs.rs fixes, or build-script compatibility. Omit purely internal refactors, test/benchmark reorganization, and post-`BASE` churn.

Adapt the lead, vocabulary, and detail level to what the repository actually ships:

| Repository archetype | Primary readers | Lead with | Avoid |
| --- | --- | --- | --- |
| **Library / SDK / FFI crate** | Downstream developers & engine integrators | Breaking signatures, exhaustive enum additions, `unsafe` contracts, Cargo features, MSRV vs. dev toolchain, peer-dependency pins, lockstep crate upgrades, native/WASM ABI rebuilds, soundness/correctness fixes. | Narrating internal module shuffles or private dependency updates that do not change public API, MSRV, or runtime behavior. |
| **CLI / Developer tool** | Terminal users & CI/script authors | Commands, flags, config schemas, exit/error contracts, stdin/stdout/JSON formats, startup/throughput wins, installation and platform font/runtime defaults. | Exposing internal Rust/library crate boundaries unless users compile from source with explicit features. |
| **End-user product / App / Service** | Product users & operators | User-visible workflows, UI/output changes, defaults, data/config migrations, platform availability, and bounded limitations. | Code identifiers, internal refactors, or developer-only plumbing that users cannot act on. |
| **Hybrid monorepo** (product + library + multi-language bindings) | Both end users and host integrators | Separate end-user workflow outcomes from host/integrator `Upgrading` contracts in the root changelog; move binding-specific API symbols into each platform/package changelog. | Dumping every binding's symbol renames into the root summary, or repeating full channel/install matrices that belong in an installation guide. |

For Rust workspaces and FFI/WASM repositories, explicitly distinguish **library MSRV** from the **repository development/publishing toolchain**, and state clearly when workspace crates, native archives, or browser/WASM providers must be upgraded or rebuilt together.

When a single section (such as `Breaking Changes` or `Fixed`) exceeds roughly 8–10 bullets, use consistent subsystem or crate lead-in prefixes (matching the repository's convention, such as `WGPU:` or `**CLI fonts.**`) so readers can scan directly to their surface.

## Multi-Package, Multi-Platform, and Multi-Axis Projections

1. **Inventory all changelog owners upfront.** List the root `CHANGELOG.md` and every sub-crate, platform binding, or distribution changelog (for example `backends/*/CHANGELOG.md`, `platforms/*/CHANGELOG.md`, `distribution/*/CHANGELOG.md`).
2. **Reconcile every affected projection on release.** When finalizing a release, never leave changes that already shipped sitting under a sub-package's `## [Unreleased]` heading. If a sub-package had no user-visible delta, follow the repository's policy (either omit a section for unchanged crates or emit the required release heading when repo automation validates lockstep presence).
3. **Filter and translate for `package-projection` mode.**
   - Project only outcomes that affect that package's API, ABI/schema, runtime behavior, platform targets, or build requirements.
   - Translate symbol and option names into the target ecosystem's native casing and APIs (for example `camelCase` in Dart/JS vs. `snake_case` in Rust/Python).
   - Map version headings to the ecosystem's required syntax when automation expects it (for example SemVer `0.10.0-alpha.2` to PEP 440 `0.10.0a2` for Python).
   - Link back to the root changelog or shared upgrade guide for cross-cutting details instead of duplicating the entire root release note.
4. **Respect independent version axes.** When a monorepo ships an independently versioned wrapper or grammar (such as a Typst wrapper or Tree-sitter package), track its own tag prefix and base release, and record both the wrapper version and the bundled core version/ABI in the release heading or intro.
5. **Handle maintenance lines and partial channel delivery honestly.** On a maintenance release or partial rollout, state the maintenance baseline clearly and list deferred channels at their actual verified published versions (or link the host installation guide) so users do not assume deferred packages were updated.

## Automation Contracts and Renderer Portability

### Respect Repository Automation and `Unreleased` Lifecycle

Inspect release workflows and changelog helper scripts before editing:

- **Heading syntax and parsers**: match the exact heading pattern expected by extractors (`cargo-dist`, `tools/changelog.py`, `verify_release_changelog.py`, etc.), including brackets, date format (`YYYY-MM-DD`), and valid calendar dates.
- **`Unreleased` lifecycle varies by repository**:
  - Some repositories require keeping an empty `## [Unreleased]` as the first section even on release commits (enforced by checks like `check-unreleased`).
  - Other repositories allow `## [Unreleased]` only during development and reject it anywhere before immutable release preflight (`--require-date`), requiring every in-scope projection to start with a dated release heading.
  - Always follow the repository's verifier contract instead of assuming one rule.
- **Soft-wrap verifiers**: keep every prose paragraph and bullet on a single physical line, including trailing links and attribution, so automated soft-wrap linters never see indented continuation lines.

### Make Links, Images, and Code Blocks Portable Across Renderers

Before writing links, check every destination where the text will render:

- **Verbatim extraction to GitHub Releases or external registries** (when a script extracts a `CHANGELOG.md` section verbatim without rewriting links, or when a package changelog is displayed on crates.io, npm, PyPI, or pub.dev):
  - Repo-relative paths (`docs/COMPATIBILITY.md`, `../../../docs/...`, `docs/img.png`) and bare local anchors (`#0100---2026-11-12`) break outside the repository tree.
  - Use canonical absolute URLs: pin version-specific documentation, migration guides, and images to the release tag (`https://github.com/<owner>/<repo>/blob/<tag>/<path>`, or raw/tagged image URLs when required by the renderer), and point only intentionally live guides (such as a rolling installation/compatibility index) to the default branch.
- **Pipeline-rewritten or strictly repo-local changelogs**:
  - If release tooling rewrites repo-relative links to tagged URLs automatically, keep local convention and verify every relative path resolves from the specific file's directory (paying extra attention to nested `../../` or `../../../` depth in package changelogs).
- **Code-fence safety**:
  - When showing source examples in languages that Markdown hosts auto-render into widgets or diagrams (such as Mermaid source inside a GitHub changelog), use a plain `text` fence so readers see the literal source instead of a rendered diagram.

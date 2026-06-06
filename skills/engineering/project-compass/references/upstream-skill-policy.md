# Upstream Skill Policy

Use this policy before making external skills part of the workflow.

## Rule

The workflow must remain self-contained. Vendor an upstream skill only when it is stable, broadly
useful, legally clear, and too large to absorb as a small rule.

## Decision Matrix

| Skill | Source | Decision | Why |
|-------|--------|----------|-----|
| `autoreview` | OpenClaw agent-skills | vendored core | Structured Codex-first closeout review helper; includes reusable scripts and clear MIT licensing. |
| `diagnose` | Matt Pocock skills | candidate to vendor | Strong debugging loop; broadly reusable. |
| `tdd` | Matt Pocock skills | candidate to vendor | Good tracer-bullet test discipline. |
| `to-issues` | Matt Pocock skills | candidate to vendor | Useful when roadmap goals need issue slicing. |
| `improve-codebase-architecture` | Matt Pocock skills | candidate to vendor or keep optional | Valuable architecture vocabulary and deepening loop, but heavy UI report may not be default. |
| `zoom-out` | Matt Pocock skills | candidate to vendor | Lightweight higher-context analysis. |
| `threads` | local/unknown source | absorb pattern, do not require | Loom should own native subagent lane maps directly. |
| `review` | Matt Pocock in-progress | absorb pattern, do not vendor by default | Two-axis review is useful; upstream status is not stable. |
| `design-an-interface` | Matt Pocock deprecated | absorb pattern, do not vendor by default | Design-it-twice is useful; deprecated upstream should not become a dependency. |
| `request-refactor-plan` | Matt Pocock deprecated | absorb pattern, do not vendor by default | Tiny-commit refactor planning is useful; keep as a rule. |
| `qa` | Matt Pocock deprecated | do not vendor by default | GitHub issue workflow is too product-specific. |
| `git-guardrails-claude-code` | Matt Pocock misc | do not vendor by default | Claude-specific hook setup does not belong in Codex workflow defaults. |

## Vendoring Rules

- Record upstream URL, license, upstream path, and reason in `upstream-skills.json`.
- Use `scripts/sync_upstream_skills.py` for copying so `SOURCE.md` and `LICENSE.upstream` are written.
- Keep `sync: false` until the skill is intentionally adopted.
- Prefer absorbing prompt patterns into `loom` or `project-compass` when the useful part is small.
- Do not add deprecated or in-progress upstream skills to default install without a separate decision.

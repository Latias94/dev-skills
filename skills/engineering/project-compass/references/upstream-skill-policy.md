# Upstream Skill Policy

Use this policy before making external skills part of the workflow.

## Rule

The workflow must remain self-contained. Vendor an upstream skill only when it is stable, broadly
useful, legally clear, and too large to absorb as a small rule.

## Decision Matrix

| Skill | Source | Decision | Why |
|-------|--------|----------|-----|
| `diagnose` | Matt Pocock skills | candidate to vendor | Strong debugging loop; broadly reusable. |
| `tdd` | Matt Pocock skills | candidate to vendor | Good tracer-bullet test discipline. |
| `to-issues` | Matt Pocock skills | candidate to vendor | Useful when roadmap goals need issue slicing. |
| `improve-codebase-architecture` | Matt Pocock skills | candidate to vendor or keep optional | Valuable architecture vocabulary and deepening loop, but heavy UI report may not be default. |
| `zoom-out` | Matt Pocock skills | candidate to vendor | Lightweight higher-context analysis. |
| `threads` | local/unknown source | absorb pattern, do not require | Loom should own native subagent lane maps only in CE-unavailable fallback mode. |
| `review` | Matt Pocock in-progress | absorb pattern, do not vendor by default | Two-axis review is useful; upstream status is not stable. |
| `design-an-interface` | Matt Pocock deprecated | absorb pattern, do not vendor by default | Design-it-twice is useful; deprecated upstream should not become a dependency. |
| `request-refactor-plan` | Matt Pocock deprecated | absorb pattern, do not vendor by default | Tiny-commit refactor planning is useful; keep as a rule. |
| `qa` | Matt Pocock deprecated | do not vendor by default | GitHub issue workflow is too product-specific. |
| `git-guardrails-claude-code` | Matt Pocock misc | do not vendor by default | Claude-specific hook setup does not belong in Codex workflow defaults. |
| `ce-brainstorm`, `ce-plan`, `ce-work`, `ce-code-review`, `ce-compound` | EveryInc Compound Engineering | external plugin preferred | MIT and high quality, but the value comes from the full plugin plus custom agents. Prefer installing CE and letting Loom invoke it when available; do not vendor individual CE skills by default. |

## Vendoring Rules

- Record upstream URL, license, upstream path, and reason in `upstream-skills.json`.
- Use `scripts/sync_upstream_skills.py` for copying so `SOURCE.md` and `LICENSE.upstream` are written.
- Keep `sync: false` until the skill is intentionally adopted.
- Prefer routing to Compound Engineering over absorbing large workflow prompts. Absorb only small local safety rules into `loom` or `project-compass`.
- Do not add deprecated or in-progress upstream skills to default install without a separate decision.
- For Compound Engineering, prefer the plugin install path over vendoring single skills:
  `codex plugin marketplace add EveryInc/compound-engineering-plugin`, then install the plugin in
  Codex's `/plugins` UI, and run `bunx @every-env/compound-plugin install compound-engineering --to codex`
  when CE agents are needed. Record any future direct vendoring decision in `upstream-skills.json`.

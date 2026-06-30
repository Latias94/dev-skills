# Research Skills

Vendored research skills:

- [`last30days`](./last30days/SKILL.md)
- [`research`](./research/SKILL.md)
- [`research-add-items`](./research-add-items/SKILL.md)
- [`research-add-fields`](./research-add-fields/SKILL.md)
- [`research-deep`](./research-deep/SKILL.md)
- [`research-report`](./research-report/SKILL.md)

`last30days` is intentionally larger than the other skills because it includes its upstream research
engine, source integrations, and assets. Update it through `scripts/sync_upstream_skills.py` so
`SOURCE.md` stays current.

The `research*` skills are the Chinese Codex-oriented Deep Research workflow vendored from
`Weizhena/Deep-Research-skills`. They create an outline, add items or fields, run per-item deep
research into JSON, and generate a final Markdown report. The deep-research stages expect a Codex
`web_researcher` agent to be available; install the upstream `agents-codex` files if you want that
agent-backed flow.

# Repository Guidelines

This repository stores reusable Codex skills for large Rust projects.

## Scope

- Skills should be small, composable, and optimized for Codex.
- Do not add Claude plugin metadata unless explicitly requested.
- Prefer referencing upstream skills instead of copying their bodies.
- Keep project workflow facts in skills, references, and templates with a single clear source of truth.

## Skill Style

- Every skill must have `SKILL.md` with `name` and `description` frontmatter.
- Skill names use lowercase hyphen-case.
- Keep `SKILL.md` concise; move detailed patterns into `references/`.
- Put copyable project scaffolds in `assets/`.
- Do not add README files inside individual skill directories.

## Documentation Language

Write repository docs, skill bodies, templates, and code comments in English.
Use Chinese only in conversation unless a user-facing artifact explicitly needs it.

## Editing Rules

- Use `apply_patch` for manual file edits.
- Do not overwrite user changes.
- Do not commit unless the user confirms.
- Use Conventional Commits when committing.

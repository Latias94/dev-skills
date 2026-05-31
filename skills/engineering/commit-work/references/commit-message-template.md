# Commit Message Template

Use Conventional Commits:

```text
<type>(<scope>): <summary>

<What changed.>
<Why it changed.>

BREAKING CHANGE: <contract or migration impact>
```

## Types

- `feat`: user-facing capability or new behavior.
- `fix`: bug fix.
- `refactor`: behavior-preserving structure change.
- `test`: test-only changes.
- `docs`: documentation-only changes.
- `chore`: maintenance that does not affect runtime behavior.
- `build`: build system, dependency, or packaging changes.
- `ci`: CI workflow changes.
- `perf`: performance improvement.
- `style`: formatting-only changes.

## Rules

- Keep the summary imperative and specific.
- Explain what and why, not the command diary.
- Use a body when the scope, motivation, migration, or risk is not obvious.
- Mention validation in the final response, not in the commit subject.

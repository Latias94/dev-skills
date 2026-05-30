# Cross-Repo Coordination

Use this when a lane bundle, shared contract, or result inspection touches related repositories such
as addons, clients, plugins, or contract consumers.

## Track

- primary repo path, branch, head, and dirty state,
- related repo paths, branches, heads, and dirty states,
- contract files or generated artifacts shared across repos,
- validation commands per repo,
- merge order and rollback signal.

## Rules

- Do not treat related repos as notes; include them in the bundle or block the task.
- Keep per-repo changed scopes explicit.
- Validate each repo with its own targeted commands.
- Integrate the contract owner before dependent repos unless the project states otherwise.
- Stop when a related repo needs a user decision, new ADR, version bump, or release note.

## Output

Report repo matrix, owned/shared scopes by repo, validation per repo, integration order, blockers,
and the next Codex goal to set for each repo-specific terminal.
